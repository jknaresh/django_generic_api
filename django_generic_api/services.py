from django.apps import apps
from django.db.models import Q


def get_model_by_name(model_name):
    """Fetch a model dynamically by searching all installed apps."""
    for app_config in apps.get_app_configs():
        try:
            model = app_config.get_model(model_name)
            return model
        except LookupError:
            continue
    raise ValueError(f"Model '{model_name}' not found in any installed app.")


def fetch_data(model_name, filters=None, fields=None):
    """
    Fetches data from a dynamically retrieved model.

    :param model_name: The name of the model (case-insensitive)
    :param filters: Dictionary of filters for the query
    :param fields: List of fields to return
    """
    model = get_model_by_name(model_name)

    # Perform a query on the model
    queryset = model.objects.all()

    # Apply filters dynamically
    if filters:
        queryset = queryset.filter(**filters)

    # Select only specified fields
    if fields:
        queryset = queryset.values(*fields)

    return queryset


def apply_filters(filters):
    """Apply dynamic filters using Q objects."""
    query = Q()
    for filter_item in filters:
        operator = filter_item.get("operator")
        field_name = filter_item.get("name")
        value = filter_item.get("value")

        if operator == "eq":
            query &= Q(**{f"{field_name}__exact": value[0]})
        elif operator == "in":
            query &= Q(**{f"{field_name}__in": value})

    return query


def handle_save_input(model, record_id, save_input):
    """Handle creating or updating a record."""
    if record_id:
        instance = model.objects.get(id=record_id)
        for field, value in save_input.items():
            setattr(instance, field, value)
        instance.save()
        message = "Record updated successfully."
    else:
        instance = model.objects.create(**save_input)
        message = "Record created successfully."
    return instance, message
