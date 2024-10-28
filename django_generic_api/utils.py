import csv
import os
import time

from django.core.exceptions import FieldDoesNotExist
from pydantic import ConfigDict
from django.utils.dateparse import parse_duration
from rest_framework.throttling import AnonRateThrottle

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


def get_model_fields_with_properties(model, input_fields):
    """
    Returns a dictionary where the keys are field names and the values are a
    dictionary
    of field properties such as 'type', 'nullability', etc.

    :param model: Django model class
    :return: dict
    """
    model_meta = getattr(model, "_meta")
    field_obj = model_meta.fields
    # todo: as per input read only those fields
    required_attributes = ["null", "blank", "max_length", "default"]
    field_dict = {}
    field_properties = {}

    # todo: separate function to get field properties
    for field1 in field_obj:
        # collect properties of fields.
        field_properties["type"] = field1.get_internal_type()

        for attr in required_attributes:
            if hasattr(field1, attr):
                field_properties[attr] = getattr(field1, attr)

        field_dict[field1.attname] = field_properties
        field_properties = {}

    return field_dict


def is_fields_exist(model, fields):
    valid_fields = []
    for field in fields:
        if "__" not in field:
            valid_fields.append(field)
        else:
            fk_field, related_field = field.split("__", 1)
            try:
                model_meta = getattr(model, "_meta")  # data of model
                fk = model_meta.get_field(fk_field)  # data of fk field
                # data of fk field model
                related_model_meta = getattr(fk.related_model, "_meta")
                related_model_meta.get_field(related_field)
            except FieldDoesNotExist:
                raise ValueError(
                    {"error": f"Invalid field {field}", "code": "DGA-U001"}
                )

    model_fields = get_model_fields_with_properties(model, valid_fields)
    result = set(valid_fields) - set(model_fields.keys())
    if len(result) > 0:
        # todo: if any foreign key validate field.
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


def validate_integer_field(value):
    return int(value) if value.isdigit() else False


def validate_bool_field(value):
    return value in [
        "True",
        "False",
        "true",
        "false",
        "0",
        "1",
        True,
        False,
        0,
        1,
    ]


def validate_char_field(value):
    try:
        if isinstance(value, str):
            value.encode("utf-8")
            return True
        else:
            return False
    except UnicodeEncodeError:
        return False


FIELD_VALIDATION_MAP = {
    "IntegerField": validate_integer_field,
    "BooleanField": validate_bool_field,
    "CharField": validate_char_field,
}


def timeparse(period):
    """
    Logic to convert '10m' into seconds, e.g., 600 for 10 minutes.
    """
    if period.endswith("m"):
        return int(period[:-1]) * 60
    elif period.endswith("h"):
        return int(period[:-1]) * 3600
    elif period.endswith("d"):
        return int(period[:-1]) * 86400
    raise ValueError("Unsupported time format")


class ExtendedRateThrottle(AnonRateThrottle):
    """
    Predefining a rate limit for Anonymous user, 'anon'.
    """

    def parse_rate(self, rate):
        """
        Given the request rate string, return a two-tuple of:
        <allowed number of requests>, <period of time in seconds>
        """
        if rate is None:
            return None, None

        num, period = rate.split("/")
        num_requests = int(num)
        duration = timeparse(period)
        return num_requests, duration
