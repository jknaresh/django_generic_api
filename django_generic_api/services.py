import json
from functools import wraps
from typing import Dict, Optional

from django.apps import apps
from django.contrib.auth import get_user_model, login
from django.db.models import *
from jsonschema import validate
from pydantic import BaseModel, create_model, EmailStr
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

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
    raise ValueError(f"Invalid Model [{model_name}].")


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
                    login(request, user)
                    # todo: instead of login user user.check_password if
                    #  possible.
                    # user.check_password(request)
                except Exception as e:
                    return Response(
                        {"error": f"Authentication failed: {str(e)}"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
        return view_function(request, *args, **kwargs)

    return _wrapped_view


def get_config_schema(model):
    model_fields: Dict[str, tuple] = {}

    for field in model._meta.fields:
        field_type = None
        is_optional = field.null or field.blank
        if field.get_internal_type() == "ForeignKey":
            if not field.name.endswith("_id"):
                field.name = f"{field.name}_id"
            field.name = field.name

        # Check if the field type exists in the mapping dictionary
        for django_field, pydantic_type in DJANGO_TO_PYDANTIC_TYPE_MAP.items():
            if isinstance(field, django_field):
                if isinstance(field, ForeignKey):
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
            model_fields[field.name] = field_type

    # Dynamically create a Pydantic model
    pydantic_model = create_model(
        model.__name__ + "Pydantic",  # Name of the Pydantic model
        **model_fields,  # Model fields passed as keyword arguments
        __base__=BaseModel,  # Base class for Pydantic models
    )
    schema = pydantic_model.model_json_schema()
    return json.dumps(schema)


def validate_field_value(model, field, value):
    # todo: validate model field with data type and value length. .. etc
    return True


def fetch_data(
    model_name,
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
    :param model_name: The name of the model (case-insensitive)
    :param filters: Dictionary of filters for the query
    :param fields1: List of fields to return
    """
    model = get_model_by_name(model_name)
    if not model:
        raise ValueError(f"Model '{model_name}' not found.")

    # Perform a query on the model
    queryset = model.objects.all()

    # Apply filters dynamically
    if filters:
        query_filters = apply_filters(model, filters)
        # todo: length(query_filters) < 1
        # return empty results
        # return dict(total=0, data=[])
        queryset = queryset.filter(query_filters)

    # Select only specified fields
    queryset = queryset.values(*fields1)
    if sort:
        sort_fields = []
        prefix = "-" if sort.order_by == "desc" else ""
        sort_fields.append(f"{prefix}{sort.field}")
        queryset = queryset.order_by(*sort_fields)

    # Apply pagination AS per the input payload.
    # queryset = queryset[0:10]

    if distinct is not False:
        # Apply distinct to ensure no duplicates
        queryset = queryset.distinct()
    # Fetch the total count of the records (without pagination)
    total_records = queryset.count()

    if page_number and page_size:
        # SQL-level pagination using slicing
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        queryset = queryset[start_index:end_index]

    return dict(total=total_records, data=list(queryset))


def apply_filters(model, filters):
    """Apply dynamic filters using Q objects."""
    query = Q()
    for filter_item in filters:
        operator = filter_item.operator
        field_name = filter_item.name
        value = filter_item.value
        operation = filter_item.operation

        if not validate_field_value(model, field_name, value):
            continue
            # raise ValueError(f"Invalid value for field '{field_name}':
            # {value}")

        if operation == "or":
            if operator == "eq":
                query |= Q(**{f"{field_name}__exact": value[0]})
            elif operator == "in":
                query |= Q(**{f"{field_name}__in": value})

        elif operator == "eq":
            query &= Q(**{f"{field_name}__exact": value[0]})
        elif operator == "in":
            query &= Q(**{f"{field_name}__in": value})
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    return query


def handle_save_input(model, record_id, save_input):
    """Handle creating or updating a record."""

    schema = get_config_schema(model)
    schema = json.loads(schema)
    # info: if schema validate fails, it will throw an error
    validate(instance=save_input, schema=schema)

    if record_id:
        # todo: check change user permissions
        instance = model.objects.get(id=record_id)
        for field, value in save_input.items():
            setattr(instance, field, value)
        instance.save()
        message = "Record updated successfully."
    else:
        # todo: check add user permissions
        instance = model.objects.create(**save_input)
        message = "Record created successfully."
    return instance, message
