from django.apps import apps
from django.conf import settings


def prepare_filters(filters):
    """Unpacks filters given as list"""

    def parse_list(value):
        if value[0] == "[" and value[-1] == "]":
            return value[1:-1].split(",")
        return value

    return {k: parse_list(v) for k, v in filters.items()}


def get_scalar_data(filters):
    scalar_model = apps.get_model(settings.DASHBOARD_SCALAR_MODEL)
    return scalar_model.objects.filter(**filters)
