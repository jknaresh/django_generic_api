import json
from functools import wraps
from typing import Dict, Optional

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models import *
from pydantic import BaseModel, create_model, EmailStr
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .utils import is_fields_exist, get_model_fields_with_properties

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


class PydanticModelConfigV1:
    str_strip_whitespace = True
    extra = "forbid"


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
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


# Define your token validation function as a decorator
def validate_access_token(view_function):
    @wraps(view_function)
    def _wrapped_view(request, *args, **kwargs):

        if not request.user.is_authenticated:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token_str = auth_header.split(" ")[1]

                try:
                    # Decoding token
                    token = AccessToken(token_str)
                    user_id = token["user_id"]
                    user_model = get_user_model()
                    user = user_model.objects.get(id=user_id)
                    # todo: instead of login user user.check_password if possible.
                    # if user.check_password(password):
                    #     setattr(request, "user", user)
                    setattr(request, "user", user)
                except Exception as e:
                    return Response(
                        {"error": f"Authentication failed: {str(e)} SERV-01"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

        return view_function(request, *args, **kwargs)

    return _wrapped_view


def get_config_schema(model):
    model_fields: Dict[str, tuple] = {}

    model_meta = getattr(model, "_meta", None)
    for field1 in model_meta.fields:
        if field1.name == "id":
            continue
        field_type = None
        is_optional = field1.null or field1.blank

        # Check if the field type exists in the mapping dictionary
        for django_field, pydantic_type in DJANGO_TO_PYDANTIC_TYPE_MAP.items():
            if isinstance(field1, django_field):
                if isinstance(field1, ForeignKey):
                    related_model_pk_type = int
                    field_type = (
                        (
                            Optional[related_model_pk_type]
                            if is_optional
                            else related_model_pk_type
                        ),
                        ...,
                    )
                else:
                    field_type = (
                        (
                            Optional[pydantic_type]
                            if is_optional
                            else pydantic_type
                        ),
                        ...,
                    )
                break
        if field_type:
            model_fields[field1.column] = field_type

    # Dynamically create a Pydantic model
    pydantic_model = create_model(
        model.__name__ + "Pydantic",  # Name of the Pydantic model
        **model_fields,  # Model fields passed as keyword arguments
        __base__=BaseModel,  # Base class for Pydantic models
    )
    pydantic_model.__config__ = PydanticModelConfigV1
    return pydantic_model


def check_field_value(model, field1, value):
    is_fields_exist(model, [field1])

    model_fields = get_model_fields_with_properties(model)
    field_properties = model_fields[field1]
    field_type = field_properties["type"]

    if field_type == "IntegerField" and not value[0].isdigit():
        return False
    if field_type == "BooleanField" and value[0] not in ["True", "False"]:
        return False

    return True


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
    # todo: validate field names from payload against config
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
        # todo: length(query_filters) < 1
        # return empty results
        # return dict(total=0, data=[])
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
    for filter_item in filters:
        operator = filter_item.operator
        field_name = filter_item.name
        value = filter_item.value
        operation = filter_item.operation

        if not check_field_value(model, field_name, value):
            raise ValueError(f"Invalid data: {value}. SERV-02")

        if operation == "or":
            if operator == "eq":
                query1 |= Q(**{f"{field_name}__exact": value[0]})
            elif operator == "in":
                query1 |= Q(**{f"{field_name}__in": value})

        elif operator == "eq":
            query1 &= Q(**{f"{field_name}__exact": value[0]})
        elif operator == "in":
            query1 &= Q(**{f"{field_name}__in": value})

    return query1


def handle_save_input(model, record_id, save_input):
    """Handle creating or updating a record."""

    model_schema = get_config_schema(model)
    instances = []
    messages = []

    for saveInput in save_input:
        # Validate against schema
        try:
            # model_schema.model_validate_json(json.dumps(saveInput))
            model_schema(**saveInput)

        except Exception as e:
            error_msg = e.errors()[0].get("msg")
            error_loc = e.errors()[0].get("loc")

            raise ValueError(f"{error_msg}. {error_loc}. SERV-03")

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
                f"Record with ID {record_id} does not exist. SERV-04"
            )
        except Exception as s:
            raise TypeError(f"{str(s)}. SERV-05")

    message = list(set(messages))
    return instances, message
