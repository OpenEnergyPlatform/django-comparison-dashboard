import django_filters
from django import forms
from django.contrib.postgres.fields import ArrayField
from django.db.models import Q

from .models import ScalarData


class ScenarioFilter(django_filters.FilterSet):
    def __init__(self, chart_type: str, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        self.chart_type = chart_type

        for field in ScalarData.filters:
            qs = self.queryset.order_by().values_list(field, flat=True).distinct()
            if isinstance(getattr(ScalarData, field).field, ArrayField):
                choices = {(item, item) for sublist in qs.all() for item in sublist}
            else:
                choices = [(choice, choice) for choice in qs.all()]

            if "group" in field:
                choices = list(choices) + [("Filter all", "Filter all")]

            field_instance = django_filters.MultipleChoiceFilter(
                field_name=field,
                choices=choices,
                widget=forms.SelectMultiple(attrs={"class": "ui fluid search dropdown"}),
                lookup_expr="overlap" if isinstance(getattr(ScalarData, field).field, ArrayField) else None,
                method=self.filter_array_fields if isinstance(getattr(ScalarData, field).field, ArrayField) else None,
            )
            self.filters[field] = field_instance

    def filter_array_fields(self, queryset, name, value):
        # This allows input or output group values to be None
        if name in ("input_groups", "output_groups") and self.chart_type == "sankey":
            return queryset.filter(Q(**{f"{name}__overlap": value}) | Q(**{f"{name}__exact": []}))
        # This checks if value is present in list
        return queryset.filter(Q(**{f"{name}__overlap": value}))

    class Meta:
        model = ScalarData
        fields = []
