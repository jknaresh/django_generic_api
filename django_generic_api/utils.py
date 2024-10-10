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


# def get_model_field_names(model):
#     model_meta = getattr(model, "_meta")
#     field_obj = model_meta.fields
#
#     field_dict = {}
#     for field1 in field_obj:
#         field_dict[field1.attname] = field1
#
#     return field_dict
#
#
# def get_model_field_type(model, field1):
#     """
#     :param model:   string
#     :param field1: string
#     :return:
#     """
#     model_meta = getattr(model, "_meta")
#     field_type1 = model_meta.get_field(field1)
#     field_type = field_type1.get_internal_type()
#
#     return field_type

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
        #collecr properties of fields.
        field_properties = {
            'type': field1.get_internal_type(),
            'null': field1.null,
            'blank': field1.blank,
            'max_length': getattr(field1, 'max_length', None),
            # Only exists for certain fields
        }
        field_dict[field1.attname] = field_properties

    return field_dict


def is_fields_exist(model, fields):
    model_fields = get_model_fields_with_properties(model)
    result = set(fields) - set(model_fields.keys())
    if len(result) > 0:
        # todo: if any foreign key validate field.
        raise ValueError(f"Extra field {result}. UTI-01")
    return True
