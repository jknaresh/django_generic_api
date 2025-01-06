import base64
import csv
import datetime
import mmap
import os
import time
from decimal import Decimal
from pathlib import Path
from typing import Any, List
from uuid import UUID

from django.core.exceptions import FieldDoesNotExist
from pydantic import ConfigDict, EmailStr, AnyUrl, IPvAnyAddress
from rest_framework import status
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import (
    InvalidToken,
    TokenError,
    AuthenticationFailed,
)
import random
import string
from django.conf import settings


actions = {
    "fetch": "view",
    "save": "add",
    "edit": "change",
    "remove": "delete",
}

# Dictionary to map Django fields to Pydantic types
DJANGO_TO_PYDANTIC_TYPE_MAP = {
    "CharField": str,
    "IntegerField": int,
    "EmailField": EmailStr,
    "BooleanField": bool,
    "FloatField": float,
    "TextField": str,
    "ForeignKey": int,
    "DateField": datetime.date,
    "PositiveBigIntegerField": int,
    "CommaSeparatedIntegerField": str,
    "ImageField": str,
    "BigAutoField": int,
    "SlugField": str,
    "FileField": str,
    "FilePathField": str,
    "URLField": AnyUrl,
    "AutoField": int,
    "UUIDField": UUID,
    "PositiveIntegerField": int,
    "PositiveSmallIntegerField": int,
    "SmallIntegerField": int,
    "BigIntegerField": int,
    "BinaryField": bytes,
    "IPAddressField": IPvAnyAddress,
    "GenericIPAddressField": IPvAnyAddress,
    "DecimalField": Decimal,
    "NullBooleanField": bool,
    "DurationField": datetime.timedelta,
    "DateTimeField": datetime.datetime,
    "TimeField": datetime.time,
    "SmallAutoField": int,
    "JSONField": dict,
    "Field": Any,
    "ManyToManyField": List[int],
    "OneToOneField": int,
}


class PydanticConfigV1:
    """
    Custom configuration for pydantic objects.
    """

    model_config = ConfigDict(
        extra="forbid",  # Forbid extra fields
        str_strip_whitespace=True,  # Remove white spaces
    )


def make_permission_str(model, action):
    """
    Returns a permission string.

    param : model (Django model), action: string(fetch, save, edit, remove).
    returns : permission string as '<app_name>.<action>_<model_name>' format.
    """
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

    if field_list:
        # info: read only user given fields in filters.name
        fields = [model_meta.get_field(fld) for fld in field_list]
    else:
        fields = model_meta.fields

    field_dict = {}

    # info: Retrieve field properties of each field
    for field1 in fields:
        field_properties = get_field_properties(field1)
        field_dict[field1.name] = field_properties

    return field_dict


def is_fields_exist(model, fields):
    """
    Checks if field exists in the model.
    Checks the existence of a foreign key field in the associated model.
    Returns error if non-existing field is passed.

    param : model (Django model), fields (List of fields).
    returns : True / Error.
    """

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
    """
    Generates a timestamp encoded token.

    param : user_id (int)
    returns : encoded token
    """
    timestamp = int(time.time())
    token = f"{user_id}:{timestamp}"
    encoded_token = base64.urlsafe_b64encode(token.encode()).decode()

    return encoded_token


def store_user_ip(user_id, user_ip):
    """
    Writes user IP address to a text file.

    param : user_id (int), user_ip (string)
    returns : None
    """
    csv_file_path = os.path.join(os.getcwd(), "user_ips.csv")

    file_exists = os.path.isfile(csv_file_path)

    with open(csv_file_path, mode="a+", newline="") as csvfile:
        writer = csv.writer(csvfile)

        if not file_exists:
            writer.writerow(["user_id", "user_ip"])

        writer.writerow([user_id, user_ip])


def custom_exception_handler(exc, context):
    """
    Generates a custom DRF error response instead of the default error response.

    param : exc (Exception), context (dict)
    returns : Response
    """
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled):
        response = Response(
            {
                "error": "Too many requests. Please try after sometime.",
                "code": "DGA-U003",
            },
            status=exc.status_code,
        )

    if isinstance(exc, (InvalidToken, TokenError)):
        return Response(
            {
                "error": "Invalid Token.",
                "code": "DGA-U004",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, AuthenticationFailed):
        return Response(
            {
                "error": "Invalid token format.",
                "code": "DGA-U005",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return response


def is_valid_email_domain(domain):
    """
    Checks if the email domain is valid or not.

    param : domain (string)
    returns : True / False
    """
    base_path = Path(__file__).resolve().parent
    domain_file = base_path / "valid_domains.txt"
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
    }
    if getattr(field1, "max_length", None):
        field_properties["max_length"] = getattr(field1, "max_length", None)
    if getattr(field1, "default", None):
        field_properties["default"] = field1.get_default()

    return field_properties


def random_digit_challenge():
    """
    Generates a challenge for Captcha api with random digits (0-9).
    """

    length = getattr(settings, "CAPTCHA_LENGTH", 4)
    ret = ""
    for i in range(length):
        ret += str(random.randint(0, 9))
    return ret, ret


def random_lowercase_challenge():
    """
    Generates a challenge for Captcha api with random lowercase letters (a-z).
    """
    length = getattr(settings, "CAPTCHA_LENGTH", 4)
    ret = ""
    for i in range(length):
        ret += random.choice(string.ascii_lowercase)
    return ret, ret


def random_uppercase_challenge():
    """
    Generates a challenge for Captcha api with random uppercase letters (A-Z).
    """
    length = getattr(settings, "CAPTCHA_LENGTH", 4)
    ret = ""
    for i in range(length):
        ret += random.choice(string.ascii_uppercase)
    return ret, ret


def mixed_digit_lowercase_challenge():
    """
    Generates a challenge for Captcha api with random digits (0-9) and lowercase letters (a-z).
    """
    length = getattr(settings, "CAPTCHA_LENGTH", 4)
    ret = ""
    for i in range(length):
        ret += random.choice(string.digits + string.ascii_lowercase)
    return ret, ret


def mixed_digit_uppercase_challenge():
    """
    Generates a challenge for Captcha api with random digits (0-9) and uppercase letters (A-Z).
    """
    length = getattr(settings, "CAPTCHA_LENGTH", 4)
    ret = ""
    for i in range(length):
        ret += random.choice(string.digits + string.ascii_uppercase)
    return ret, ret
