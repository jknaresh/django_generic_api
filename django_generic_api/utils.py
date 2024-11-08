import csv
import os
import time

from django.core.exceptions import FieldDoesNotExist
from pydantic import ConfigDict
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework.views import exception_handler
import mmap

actions = {
    "fetch": "view",
    "save": "add",
    "edit": "change",
    "remove": "delete",
}


class PydanticConfigV1:
    model_config = ConfigDict(
        extra="forbid",  # Forbid extra fields
        str_strip_whitespace=True,  # Remove white spaces
    )


def make_permission_str(model, action):
    model_meta = getattr(model, "_meta")
    action = actions.get(action)
    permission = f"{model_meta.app_label}.{action}_{model_meta.model_name}"

    return permission


def get_model_fields_with_properties(model, field_list=None):
    """
    Returns a dictionary where the keys are field names and the values are a
    dictionary
    of field properties such as 'type', 'nullability', etc.

    :param model: Django model class
    :return: dict
    """
    model_meta = getattr(model, "_meta")

    fields = []
    if field_list:
        # info: read only user given fields in filters.name
        fields.append(model_meta.get_field(field_list))
    else:
        fields = model_meta.fields

    field_dict = {}

    # info: Retrieve field properties of each field
    for field1 in fields:
        field_properties = get_field_properties(field1)
        field_dict[field1.name] = field_properties

    return field_dict


def is_fields_exist(model, fields):
    valid_fields = []
    for field in fields:
        if not field.__contains__("__"):
            valid_fields.append(field)
        else:
            # Validate if the fk field exists
            fk_field, related_field = field.split("__", 1)
            try:
                model_meta = getattr(model, "_meta")  # data of model
                fk = model_meta.get_field(fk_field)  # data of fk field
                # data of fk field model
                related_model_meta = getattr(fk.related_model, "_meta")
                related_model_meta.get_field(related_field)
            except FieldDoesNotExist:
                raise ValueError(
                    {
                        "error": f"Invalid foreign field {field}",
                        "code": "DGA-U001",
                    }
                )

    model_fields = get_model_fields_with_properties(model)
    result = set(valid_fields) - set(model_fields.keys())
    if len(result) > 0:
        raise ValueError(
            {"error": f"Extra field {result}", "code": "DGA-U002"}
        )
    return True


def registration_token(user_id):
    timestamp = int(time.time())
    token = f"{user_id}:{timestamp}"
    return token


def store_user_ip(user_id, user_ip):
    csv_file_path = os.path.join(os.getcwd(), "user_ips.csv")

    file_exists = os.path.isfile(csv_file_path)

    with open(csv_file_path, mode="a+", newline="") as csvfile:
        writer = csv.writer(csvfile)

        if not file_exists:
            writer.writerow(["user_id", "user_ip"])

        writer.writerow([user_id, user_ip])


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled):
        response = Response(
            {
                "error": "Too many requests. Please try after sometime.",
                "code": "DGA-U003",
            },
            status=exc.status_code,
        )
    return response


def is_valid_domain(domain):

    domain_file = "valid_domains.txt"
    domain_bytes = domain.lower().encode("utf-8")

    with open(domain_file, "rb", 0) as file:
        s = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
        if s.find(domain_bytes) != -1:
            return True

    return False


def get_field_properties(field1):
    """
    Retrieve field properties like 'type','null','blank',
    'max_length', 'default'

    param : Django field instance
    return : dict with field properties
    """
    field_properties = {
        "type": field1.get_internal_type(),
        "null": field1.null,
        "blank": field1.blank,
        "max_length": getattr(field1, "max_length", None),
        "default": getattr(field1, "default", None),
    }

    return field_properties
