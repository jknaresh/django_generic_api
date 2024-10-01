actions = {
    "fetch": "view",
    "save": "add",
    "edit": "change",
    "remove": "delete",
}


def make_permission_str(model, action):
    model_meta = getattr(model, "_meta", None)
    model_name = model.__name__.lower()
    action = actions.get(action)
    permission = f"{model_meta.app_label}.{action}_{model_name}"

    return permission
