import django_filters
from django import forms
from django.contrib.postgres.fields import ArrayField

from .models import ScalarData


class ScenarioFilter(django_filters.FilterSet):
    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        for field in ScalarData.filters:
            qs = self.queryset.order_by().values_list(field, flat=True).distinct()
            if isinstance(getattr(ScalarData, field).field, ArrayField):
                choices = {(item, item) for sublist in qs.all() for item in sublist}
            else:
                choices = [(choice, choice) for choice in qs.all()]
            field_instance = django_filters.MultipleChoiceFilter(
                field_name=field,
                choices=choices,
                widget=forms.SelectMultiple(attrs={"class": "form-control"}),
                lookup_expr="overlap" if isinstance(getattr(ScalarData, field).field, ArrayField) else None,
                method=self.filter_array_fields if isinstance(getattr(ScalarData, field).field, ArrayField) else None,
            )
            self.filters[field] = field_instance

    @staticmethod
    def filter_array_fields(queryset, name, value):
        return queryset.filter(**{f"{name}__overlap": value})

    class Meta:
        model = ScalarData
        fields = []
