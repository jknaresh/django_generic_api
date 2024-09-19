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


def fetch_data(
    model_name,
    filters=None,
    fields=None,
    page_number=1,
    page_size=5,
    sort=None,
):
    """
    Fetches data from a dynamically retrieved model.

    :param records_per_page:
    :param page_number:
    :param model_name: The name of the model (case-insensitive)
    :param filters: Dictionary of filters for the query
    :param fields: List of fields to return
    """
    model = get_model_by_name(model_name)
    if not model:
        raise ValueError(f"Model '{model_name}' not found.")

    # Perform a query on the model
    queryset = model.objects.all()

    # Apply filters dynamically
    if filters:
        query_filters = apply_filters(filters)
        queryset = queryset.filter(query_filters)

    # Select only specified fields
    queryset = queryset.values(*fields)

    if sort:
        sort_fields = []
        prefix = "-" if sort.order_by == "desc" else ""
        sort_fields.append(f"{prefix}{sort.field}")
        queryset = queryset.order_by(*sort_fields)

    # Apply pagination AS per the input payload.
    # queryset = queryset[0:10]

    # Apply distinct to ensure no duplicates
    queryset = queryset.distinct()

    # SQL-level pagination using slicing
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    paginated_queryset = queryset[start_index:end_index]

    # Fetch the total count of the records (without pagination)
    total_records = queryset.count()

    return dict(total=total_records, data=list(paginated_queryset))


def apply_filters(filters):
    """Apply dynamic filters using Q objects."""
    query = Q()
    for filter_item in filters:
        operator = filter_item.operator
        field_name = filter_item.name
        value = filter_item.value

        if operator == "eq":
            query &= Q(**{f"{field_name}__exact": value[0]})
        elif operator == "in":
            query &= Q(**{f"{field_name}__in": value})
        else:
            raise ValueError(f"Unsupported operator: {operator}")

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
