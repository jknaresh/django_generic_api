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


def get_model_field_names(model):
    model_meta = getattr(model, "_meta")
    field_obj = model_meta.fields

    field_dict = {}
    for field1 in field_obj:
        field_dict[field1.attname] = field1

    return field_dict


def get_model_field_type(model, field1):
    """
    :param model:
    :param field1: string
    :return:
    """
    model_meta = getattr(model, "_meta")
    field_type1 = model_meta.get_field(field1)
    field_type = field_type1.get_internal_type()

    return field_type


def is_fields_exist(model, fields):
    model_fields = get_model_field_names(model)
    result = set(fields) - set(model_fields.keys())
    if len(result) > 0:
        # todo: if any foreign key validate field.
        raise ValueError(f"Extra field {result}.")
    return True
