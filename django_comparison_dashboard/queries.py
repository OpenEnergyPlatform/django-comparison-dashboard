from django.apps import apps
from django.conf import settings
from django.db.models import Sum


def get_scalar_data(filters, group_by):
    scalar_model = apps.get_model(settings.DASHBOARD_SCALAR_MODEL)
    return scalar_model.objects.filter(**filters).values(*group_by).annotate(Sum("value"))
