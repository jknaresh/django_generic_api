from typing import Dict, Optional

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q
from pydantic import (
    create_model,
    Field,
)
from django.db.models.fields.related import ForeignKey
from pydantic.config import ConfigDict
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .utils import (
    make_permission_str,
    get_model_fields_with_properties,
    is_fields_exist,
    DJANGO_TO_PYDANTIC_TYPE_MAP,
    str_field_to_model_field,
    error_response,
    raise_exception,
)

DEFAULT_APPS = {
    "django.contrib.admin": True,
    "django.contrib.auth": True,
    "django.contrib.contenttypes": True,
    "django.contrib.sessions": True,
    "django.contrib.messages": True,
    "django.contrib.staticfiles": True,
}


def get_model_by_name(model_name):
    """
    Fetches a model dynamically by searching through all installed apps.
    The expected formats for model_name are: 'app_name.model_name' or
    'model_name'.
    If the model is found, the function returns the model.
    If the model is not found, it raises an error.

    param : model_name
    return : model object/error
    """
    if model_name.__contains__("."):
        try:
            model = apps.get_model(model_name)
            if model:
                return model
        except LookupError:
            raise_exception(error="Model not found", code="DGA-S013")
    for app_config in apps.get_app_configs():
        if not DEFAULT_APPS.get(app_config.name):
            model = app_config.models.get(model_name.lower())
            if model:
                return model
    raise_exception(error="Model not found", code="DGA-S012")


def generate_token(user):
    """
    Generates an auth access token and a refresh token for user authentication.

    param : Django user instance
    returns : A pair of access anf refresh token
    """
    refresh = RefreshToken.for_user(user)
    return [
        {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    ]


def get_model_config_schema(model, fields=None):
    """
    Converts a Django ORM model into a Pydantic model object.

    The resulting Pydantic model includes fields with their corresponding
    types, `max_length`, `default` constraints (if applicable), and an
    indication of whether fields are required.

    :param fields:
    :param model: Django model class to convert into a Pydantic model.
    """
    model_fields: Dict[str, tuple] = {}

    # info: validates nested fields(foreign key fields for time being "__")
    model_meta = getattr(model, "_meta", None)

    if fields:
        fields = str_field_to_model_field(model, fields)

    if not fields:
        fields = model_meta.fields

    for field1 in fields:
        if field1.name == "id":
            continue

        field_constraints = {}

        is_optional = field1.null or field1.blank or field1.has_default()
        default_value = field1.get_default() if field1.has_default() else None

        django_field_type = field1.get_internal_type()

        # Retrieve the Pydantic type from the mapping
        if not DJANGO_TO_PYDANTIC_TYPE_MAP.get(django_field_type):
            return error_response(
                error=f"Field type mapping not found for: " f"{field1.name}",
                code="DGA-S001",
            )

        mapped_type = DJANGO_TO_PYDANTIC_TYPE_MAP.get(django_field_type)

        if django_field_type == "ForeignKey":
            related_model_pk_type = int  # Assuming int PK for related fields
            field_type = (
                Optional[related_model_pk_type]
                if is_optional
                else related_model_pk_type
            )
        else:
            field_type = Optional[mapped_type] if is_optional else mapped_type

        # Assigning attribute `max_length` if they exist for the field
        if hasattr(field1, "max_length"):
            field_constraints["max_length"] = field1.max_length

        model_fields[field1.name] = (
            field_type,
            Field(default=default_value, **field_constraints),
        )

    config_dict = ConfigDict(
        title=model.__name__,
        extra="forbid",  # Forbid extra fields
        str_strip_whitespace=True,  # Remove white spaces from strings
    )

    # Dynamically create a Pydantic model
    pydantic_model = create_model(
        model.__name__ + "Pydantic",  # Name of the Pydantic model
        **model_fields,  # Model fields passed as keyword arguments
        __config__=config_dict,
    )

    return pydantic_model


def check_field_value(model, field1, value):
    """
    Check if the user given field exists in the model.
    Retrieve the field's properties (such as null, blank, max_length, default).
    Verify if the field accepts null as a valid input.
    Confirm that the value is suitable for insertion into the field.

    param : model, fields, value
    return : True/False
    """
    is_fields_exist(model, [field1])

    model_fields = get_model_fields_with_properties(model, [field1])
    field_properties = model_fields[field1]
    if field_properties.get("null") and value[0] is None:
        return True

    model_meta = getattr(model, "_meta")
    field_instance = model_meta.get_field(field1)

    for value_i in value:
        try:
            field_instance.get_prep_value(value_i)
        except (ValueError, ValidationError):
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
    # info: validate field names from payload against model fields
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
    """
    Apply dynamic filters using Q objects.
    Raises error if 'filters.value' is not suitable for 'filters.name' field
    type.
    Supported operators are (eq, in, not, gt, like, ilike).

    param : model (Django model), filters (List of filter objects).
    returns : String representation of Q object / ValueError.
    """
    query1 = Q()
    last_logical_operation = "and"
    for filter_item in filters:
        operator = filter_item.operator
        field_name = filter_item.name
        value = filter_item.value
        operation = filter_item.operation

        if not check_field_value(model, field_name, value):
            raise_exception(
                error=f"Invalid data: {value} for {field_name}",
                code="DGA-S002",
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
        elif operator == "like":
            condition1 = Q(**{f"{field_name}__contains": value[0]})
        elif operator == "ilike":
            condition1 = Q(**{f"{field_name}__icontains": value[0]})

        if last_logical_operation == "or":
            query1 |= condition1
        else:
            query1 &= condition1
        last_logical_operation = operation.value

    return query1


def handle_save_input(model, record_id, save_input):
    """
    Create or Update a record.
    Gets a json schema of model configuration.
    Returns Error if record_id exists when length of save_input is greater
    than 1.
    Returns Error if non-existing fields are passed.
    Fills with defaults value for a field when value is not given and
    null=True.
    Returns Error if value is not suitable to insert/update in a field type.
    Returns Error if non-existing record id is passed.
    When save_input is correct:
        - Updates the record if record_id is passed.
        - Creates a new record if record_id is null.

    param : model (Django model), record_id (null/integer), save_input (List
    of dict).
    return : Success message / Error message.
    """

    model_schema_pydantic_model = get_model_config_schema(model)

    instances = []
    messages = []

    if record_id and len(save_input) > 1:
        raise_exception(
            error="Only 1 record to update at once", code="DGA-S003"
        )

    for saveInput in save_input:

        # Validate against schema
        try:
            model_schema_pydantic_model(**saveInput)

        except Exception as e:
            error_msg = e.errors()[0].get("msg")
            error_loc = e.errors()[0].get("loc")

            raise_exception(error=f"{error_msg}. {error_loc}", code="DGA-S004")

        for field_name, value in list(saveInput.items()):
            model_meta = getattr(model, "_meta", None)
            model_field = model_meta.get_field(field_name)

            if (
                model_field.has_default()
                and not value
                and value is not False
                and not model_field.null
            ):
                saveInput.pop(field_name)

            try:
                model_field.get_prep_value(value)
            except Exception as e:
                raise_exception(error=e, code="DGA-S005")

            if isinstance(model_field, ForeignKey):
                saveInput[model_field.attname] = saveInput.pop(field_name)

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
            raise_exception(
                error=f"Record with (ID) {record_id} does not exist",
                code="DGA-S006",
            )
        except Exception as e:
            raise_exception(error=e.args[0], code="DGA-S007")
    message = list(set(messages))
    return instances, message


def handle_user_info_save_input(save_input, user_id):
    """
    1. Checks if user has configured Fields (USER_INFO_FIELDS) to be accessed in user model.
    2. Creates a pydantic model with user given fields in (USER_INFO_FIELDS).
    3. Pydantic model level validation.
    4. Checks if the value is suitable to be inserted in respective field.
    5. If values are valid for fields, updates the field values.

    :param save_input:
    :param user_id:
    :return:
    """

    if not hasattr(settings, "USER_INFO_FIELDS"):
        raise_exception(
            error="Set setting for 'USER_INFO_FIELDS' to update "
            "information.",
            code="DGA-S008",
        )

    user_info_pydantic_model = get_model_config_schema(
        get_user_model(), fields=settings.USER_INFO_FIELDS
    )

    try:
        user_info_pydantic_model(**save_input)
    except Exception as e:
        error_msg = e.errors()[0].get("msg")
        error_loc = e.errors()[0].get("loc")

        raise_exception(error=f"{error_msg}. {error_loc}", code="DGA-S009")

    for key, value in list(save_input.items()):
        model_meta = getattr(get_user_model(), "_meta", None)
        model_field = model_meta.get_field(key)

        if (
            model_field.has_default()
            and not value
            and value is not False
            and not model_field.null
        ):
            save_input.pop(key)

        try:
            model_field.get_prep_value(value)
        except Exception as e:
            raise_exception(error=e, code="DGA-S010")

        if isinstance(model_field, ForeignKey):
            save_input[model_field.attname] = save_input.pop(key)

    user_model = get_user_model()
    user = user_model.objects.get(id=user_id)

    try:
        for key, value in list(save_input.items()):
            setattr(user, key, value)
        user.save()
        return f"{user.username}'s info is updated"
    except Exception as e:
        if isinstance(e, IntegrityError):
            raise_exception(
                error="Invalid foreign key constraint", code="DGA-S014"
            )
        else:
            raise_exception(error=str(e), code="DGA-S015")


def fetch_user_info(user):
    """
    1. Checks if user has configured Fields (USER_INFO_FIELDS) to be accessed in user model.
    2. Receives model fields of the given fields in (USER_INFO_FIELDS).
    3. Create a dictionary mapping field names to their corresponding values from the user object.

    :param user:
    :return:
    """

    if not hasattr(settings, "USER_INFO_FIELDS"):
        raise_exception(
            error="Set setting for 'USER_INFO_FIELDS' to update "
            "information.",
            code="DGA-S011",
        )

    fields = str_field_to_model_field(
        model=get_user_model(), fields=settings.USER_INFO_FIELDS
    )

    user_info = {}

    for field in fields:
        user_info[field.attname] = getattr(user, field.attname, None)

    return dict(data=user_info)


def check_user_related_configurations(model_name, key):
    """
    Checks if user related models system settings are properly configured or not.
    - Checks if user given model in configured in system or not.
    - Checks if user passed model actually exists or not.
    - Checks if fields are configured in system.
    - Checks if user_related_field is configured or not.
    - Checks if user_related_field is linked to auth user model or not.

    :param model_name:
    :param key:
    :return:
    """
    rel_type, method = key.split(".")
    field = {"POST": "fetch_fields", "PUT": "save_fields"}.get(method)
    config_map = {
        "1-1": getattr(settings, "ONE_TO_ONE_MODELS", {}),
    }

    if not config_map.get(rel_type):
        raise_exception(
            error="Set settings for User Related models.", code="DGA-S019"
        )

    configured_model = config_map.get(rel_type, {}).get(model_name)
    if configured_model is None:
        raise_exception(
            error=f"{model_name} is not configured.", code="DGA-S020"
        )

    model = get_model_by_name(model_name)
    model_meta = getattr(model, "_meta", None)

    configured_fields = configured_model.get(field)
    if configured_fields is None:
        raise_exception(error=f"{field} must be configured.", code="DGA-S021")

    user_related_field = configured_model.get("user_related_field")
    if user_related_field is None:
        raise_exception(
            error="`user_related_field` must be configured.",
            code="DGA-S018",
        )

    # Checks if system `user_related_field` is Fk or not.
    # Retrieves the fk model.
    try:
        related_model = model_meta.get_field(user_related_field).related_model
    except Exception as e:
        raise_exception(error=e.args[0], code="DGA-S023")

    if related_model != get_user_model():
        raise_exception(
            error=f"{user_related_field} is not linked to auth model.",
            code="DGA-S024",
        )

    return model, configured_fields, user_related_field


def fetch_one_to_one(model_name, fields, user_id, key):
    """
    Fetches all records of authenticated user from system configured 1-1 and 1-M model.
    - Checks if system settings are properly configured or not.
    - Checks if system configured fields exist in model.
    - Raises an error if the payload contains undefined fields.
    - Fetches records related to user in system model.

    :param model_name:
    :param fields:
    :param user_id:
    :param key:
    :return:
    """

    # Check if system settings are properly configured.
    model, configured_fields, user_related_field = (
        check_user_related_configurations(model_name, key)
    )

    # Check if fields in settings actually exist in model or not.
    is_fields_exist(model, configured_fields)

    # Check if user has passed extra fields in payload.
    extra_fields = set(fields) - set(configured_fields)
    if len(extra_fields) > 0:
        raise_exception(
            error=f"Unknown fields {extra_fields} in payload",
            code="DGA-S027",
        )

    perm_str = make_permission_str(model, action="fetch")
    user = get_user_model().objects.get(id=user_id)
    if not user.has_perm(perm_str):
        raise_exception(
            error="Access is restricted to this model", code="DGA-S029"
        )

    try:
        # Filters records with user id from request.user.id.
        # Returns specific fields instead of full objects.
        queryset = model.objects.filter(
            **{user_related_field: user_id}
        ).values(*fields)

        if not queryset.exists():
            return "No data found."

        total_records = queryset.count()
        return dict(total=total_records, data=list(queryset))
    except Exception as e:
        raise_exception(error=str(e), code="DGA-S028")


def save_one_to_one(model_name, save_input, user_id, key):
    """
    1. Checks if user has configured profile related fields or not.
    2. Generates a pydantic model for the configured user profile fields.
    3. Pydantic model level validation is done.
    4. Checks if the value is suitable to be inserted in respective field.
    4. Retrieves profile related with the user.
    5. If user has a profile, it is updated with the values.
    6. If user does not have a profile, it creates a profile for user.

    :param model_name:
    :param save_input:
    :param user_id:
    :param key:
    :return:
    """

    # Check if system settings are properly configured.
    model, configured_fields, user_related_field = (
        check_user_related_configurations(model_name, key)
    )

    # Throw error if `save_fields` contains th user related field.
    if configured_fields.__contains__(user_related_field):
        raise_exception(
            error="The USER field cannot be included in save_fields.",
            code="DGA-S026",
        )

    user_profile_pydantic_model = get_model_config_schema(
        model, fields=configured_fields
    )

    model_meta = getattr(model, "_meta", None)

    try:
        user_profile_pydantic_model(**save_input[0])
    except Exception as e:
        error_msg = e.errors()[0].get("msg")
        error_loc = e.errors()[0].get("loc")

        raise_exception(error=f"{error_msg}. {error_loc}", code="DGA-S017")

    for key, value in list(save_input[0].items()):
        model_field = model_meta.get_field(key)

        if (
            model_field.has_default()
            and not value
            and value is not False
            and not model_field.null
        ):
            save_input[0].pop(key)

        try:
            model_field.get_prep_value(value)
        except Exception as e:
            raise_exception(error=e, code="DGA-S016")

        if isinstance(model_field, ForeignKey):
            save_input[0][model_field.attname] = save_input[0].pop(key)

    user = get_user_model().objects.get(id=user_id)
    user_field = model_meta.get_field(user_related_field)

    user_profile = model.objects.filter(
        **{user_related_field: user_id}
    ).first()

    action_str = "edit" if user_profile else "save"

    # Check is user has permission to add or change.
    perm_str = make_permission_str(model, action=action_str)
    user = get_user_model().objects.get(id=user_id)
    if not user.has_perm(perm_str):
        raise_exception(
            error="Access is restricted to this model", code="DGA-S030"
        )

    try:
        if user_profile:
            for key, value in list(save_input[0].items()):
                setattr(user_profile, key, value)
            user_profile.save()
            message = f"{user.username}'s profile is updated"
            return (
                message,
                status.HTTP_200_OK,
            )
        else:
            save_input[0][user_field.attname] = user_id
            user_profile = model.objects.create(**save_input[0])
            message = f"{user.username}'s profile is created"
            return (
                message,
                status.HTTP_201_CREATED,
            )
    except Exception as e:
        if isinstance(e, IntegrityError):
            raise_exception(
                error="Invalid foreign key constraint", code="DGA-S022"
            )
        else:
            raise_exception(error=str(e), code="DGA-S025")
