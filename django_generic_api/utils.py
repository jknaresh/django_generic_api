import time
from django.db.models.fields import NOT_PROVIDED


actions = {
    "fetch": "view",
    "save": "add",
    "edit": "change",
    "remove": "delete",
}


def make_permission_str(model, action):
    model_meta = getattr(model, "_meta")
    action = actions.get(action)
    permission = f"{model_meta.app_label}.{action}_{model_meta.model_name}"

    return permission


def get_model_fields_with_properties(model):
    """
    Returns a dictionary where the keys are field names and the values are a dictionary
    of field properties such as 'type', 'nullability', etc.

    :param model: Django model class
    :return: dict
    """
    model_meta = getattr(model, "_meta")
    field_obj = model_meta.fields

    field_dict = {}
    for field1 in field_obj:
        # collecr properties of fields.
        field_properties = {
            "type": field1.get_internal_type(),
            "null": field1.null,
            "blank": field1.blank,
            "max_length": getattr(field1, "max_length", None),
            "default": None if field1.default is NOT_PROVIDED else field1.default,
        }
        field_dict[field1.attname] = field_properties

    return field_dict


def is_fields_exist(model, fields):
    model_fields = get_model_fields_with_properties(model)
    result = set(fields) - set(model_fields.keys())
    if len(result) > 0:
        # todo: if any foreign key validate field.
        raise ValueError(f"Extra field {result}", "UNKNOWN_FIELD")
    return True


def registration_token(user_id):
    timestamp = int(time.time())
    token = f"{user_id}:{timestamp}"
    return token


def validate_integer_field(value):
    return int(value) if value.isdigit() else False


def validate_bool_field(value):
    return value in ["True", "False", "true", "false", "0", "1"]


def validate_char_field(value):
    return True
