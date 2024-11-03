from functools import wraps
from typing import Dict, Optional

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models import (
    Q,
    IntegerField,
    CharField,
    EmailField,
    BooleanField,
    FloatField,
    TextField,
    ForeignKey,
)
from django.http import JsonResponse
from pydantic import BaseModel, create_model, EmailStr, Field
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .utils import (
    get_model_fields_with_properties,
    is_fields_exist,
    PydanticConfigV1,
    FIELD_VALIDATION_MAP,
)

DEFAULT_APPS = {
    "django.contrib.admin": True,
    "django.contrib.auth": True,
    "django.contrib.contenttypes": True,
    "django.contrib.sessions": True,
    "django.contrib.messages": True,
    "django.contrib.staticfiles": True,
}

# Define a dictionary to map Django fields to Pydantic types
DJANGO_TO_PYDANTIC_TYPE_MAP = {
    CharField: str,
    IntegerField: int,
    EmailField: EmailStr,
    BooleanField: bool,
    FloatField: float,
    TextField: str,
    ForeignKey: int,
}


def get_model_by_name(model_name):
    """Fetch a model dynamically by searching all installed apps."""
    for app_config in apps.get_app_configs():
        if not DEFAULT_APPS.get(app_config.name):
            model = app_config.models.get(model_name.lower())
            if model:
                return model
    raise ValueError


def generate_token(user):
    refresh = RefreshToken.for_user(user)
    return [
        {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    ]


# Define your token validation function as a decorator
def validate_access_token(view_function):
    @wraps(view_function)
    def _wrapped_view(request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                auth_header = request.headers.get("Authorization")
                if not auth_header:
                    raise AuthenticationFailed(
                        {"detail": "Unauthorized access", "code": "DGA-S001"}
                    )
                if auth_header and not auth_header.startswith("Bearer "):
                    raise AuthenticationFailed(
                        {"detail": "Invalid Token", "code": "DGA-S002"}
                    )
                token_str = auth_header.split(" ")[1]

                token = AccessToken(token_str)  # Decoding token
                user_id = token["user_id"]
                user_model = get_user_model()
                user = user_model.objects.get(id=user_id)
                setattr(request, "user", user)
        except AuthenticationFailed as e:
            return JsonResponse(
                {
                    "error": e.detail["detail"],
                    "code": e.detail["code"],
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return JsonResponse(
                {
                    "error": f"Authentication failed: {str(e)}",
                    "code": "DGA-S003",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return view_function(request, *args, **kwargs)

    return _wrapped_view


def get_model_config_schema(model):
    """
    Converts a Django ORM model into a Pydantic model object.

    The resulting Pydantic model includes fields with their corresponding
    types, `max_length,default` constraints (if applicable), and an
    indication of whether fields are required.

    :param model: Django model class to convert into a Pydantic model.
    """
    model_fields: Dict[str, tuple] = {}

    # info: validates nested fields(foreign key fields for time being "__")
    model_meta = getattr(model, "_meta", None)

    for field1 in model_meta.fields:
        if field1.name == "id":
            continue

        field_type = None
        field_constraints = {}

        is_optional = field1.null or field1.blank or field1.has_default()
        default_value = field1.default if field1.has_default() else None

        # Check if the field type exists in the mapping dictionary
        for django_field, pydantic_type in DJANGO_TO_PYDANTIC_TYPE_MAP.items():
            if isinstance(field1, django_field):
                if isinstance(field1, ForeignKey):
                    related_model_pk_type = (
                        int  # Assuming PK type as int for related fields
                    )
                    field_type = (
                        Optional[related_model_pk_type]
                        if is_optional
                        else related_model_pk_type
                    )
                else:
                    field_type = (
                        Optional[pydantic_type]
                        if is_optional
                        else pydantic_type
                    )

                if (
                    hasattr(field1, "max_length")
                    and field1.max_length is not None
                ):
                    field_constraints["max_length"] = field1.max_length
                break

        if field_type:
            # Set field with default if optional, or required if no default
            if is_optional:
                model_fields[field1.column] = (
                    field_type,
                    Field(default=default_value, **field_constraints),
                )
            else:
                model_fields[field1.column] = (
                    field_type,
                    Field(
                        ..., **field_constraints
                    ),  # Required without default
                )

    # Dynamically create a Pydantic model
    pydantic_model = create_model(
        model.__name__ + "Pydantic",  # Name of the Pydantic model
        **model_fields,  # Model fields passed as keyword arguments
        __base__=BaseModel,  # Base class for Pydantic models
    )
    pydantic_model.__config__ = PydanticConfigV1
    return pydantic_model


def check_field_value(model, field1, value):
    is_fields_exist(model, [field1])

    model_fields = get_model_fields_with_properties(model, [field1])
    field_properties = model_fields[field1]
    if field_properties.get("null") and value[0] is None:
        return True

    field_type = field_properties["type"]
    validation_func = FIELD_VALIDATION_MAP.get(field_type)
    if not validation_func:
        return True

    is_valid_value = None
    for value_i in value:
        if not is_valid_value:
            is_valid_value = validation_func(value_i)
        else:
            is_valid_value *= validation_func(value_i)
    return is_valid_value


def fetch_data(
    model,
    filters=None,
    fields1=None,
    page_number=None,
    page_size=None,
    sort=None,
    distinct=None,
):
    """
    Fetches data from a dynamically retrieved model.

    :param distinct:
    :param sort:
    :param page_size:
    :param page_number:
    :param model: django DB Model
    :param filters: Dictionary of filters for the query
    :param fields1: List of fields to return
    """
    # info: validate field names from payload against config
    is_fields_exist(model, fields1)

    # sort field validation
    if sort:
        is_fields_exist(model, [sort.field])

    # Perform a query on the model
    queryset = model.objects.all()

    # Apply filters dynamically
    if filters:
        query_filters = apply_filters(model, filters)
        if len(query_filters.children) < 1:
            return dict(total=0, data=[])
        queryset = queryset.filter(query_filters)

    # Select only specified fields
    queryset = queryset.values(*fields1)

    # Sorting
    if sort:
        sort_fields = []
        prefix = "-" if sort.order_by == "desc" else ""
        sort_fields.append(f"{prefix}{sort.field}")
        queryset = queryset.order_by(*sort_fields)

    # Distinct
    if distinct is not False:
        # Apply distinct to ensure no duplicates
        queryset = queryset.distinct()
    # Fetch the total count of the records (without pagination)
    total_records = queryset.count()

    # pagination
    if page_number and page_size:
        # SQL-level pagination using slicing
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        queryset = queryset[start_index:end_index]

    return dict(total=total_records, data=list(queryset))


def apply_filters(model, filters):
    """Apply dynamic filters using Q objects."""
    query1 = Q()
    last_logical_operation = "and"
    for filter_item in filters:
        operator = filter_item.operator
        field_name = filter_item.name
        value = filter_item.value
        operation = filter_item.operation

        if not check_field_value(model, field_name, value):
            raise ValueError(
                {"error": f"Invalid data: {value}", "code": "DGA-S004"}
            )

        condition1 = None

        if operator == "eq":
            condition1 = Q(**{f"{field_name}__exact": value[0]})
        elif operator == "in":
            condition1 = Q(**{f"{field_name}__in": value})
        elif operator == "not":
            condition1 = ~Q(**{f"{field_name}": value[0]})
        elif operator == "gt":
            condition1 = Q(**{f"{field_name}__gt": value[0]})

        if last_logical_operation == "or":
            query1 |= condition1
        else:
            query1 &= condition1
        last_logical_operation = operation.value

    return query1


def handle_save_input(model, record_id, save_input):
    """Handle creating or updating a record."""

    model_schema_pydantic_model = get_model_config_schema(model)
    model_schema = model_schema_pydantic_model.model_json_schema()
    model_fields = set(model_schema["properties"].keys())

    instances = []
    messages = []

    if record_id and len(save_input) > 1:
        raise ValueError(
            {"error": "Only 1 record to update at once", "code": "DGA-S005"}
        )

    for saveInput in save_input:

        # info: restricts extra fields in saveInput
        results = set(saveInput.keys()) - model_fields
        if len(results) > 0:
            raise ValueError(
                {"error": f"Extra field {results}", "code": "DGA-S009"}
            )

        # Validate against schema
        try:
            model_schema_pydantic_model(**saveInput)

        except Exception as e:
            error_msg = e.errors()[0].get("msg")
            error_loc = e.errors()[0].get("loc")

            raise ValueError(
                {"error": f"{error_msg}. {error_loc}", "code": "DGA-S006"}
            )

        try:
            if record_id:
                # Fetch the instance if record_id is provided
                instance = model.objects.get(id=record_id)

                for field1, value in saveInput.items():
                    setattr(instance, field1, value)
                instance.save()
                message = "Record updated successfully."
            else:
                # Validate save_input fields for creating a new record
                instance = model.objects.create(**saveInput)
                message = "Record created successfully."

            instances.append(instance)
            messages.append(message)
        except model.DoesNotExist:
            raise ValueError(
                {
                    "error": f"Record with (ID) {record_id} does not exist",
                    "code": "DGA-S007",
                }
            )
        except Exception:
            raise ValueError({"error": "Invalid ID", "code": "DGA-S008"})

    message = list(set(messages))
    return instances, message
