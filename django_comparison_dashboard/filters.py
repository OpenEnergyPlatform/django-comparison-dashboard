import django_filters
from django import forms

from .models import ScalarData


class ScenarioFilter(django_filters.FilterSet):
    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        for field in ScalarData.filters:
            qs = self.queryset.order_by().values_list(field, flat=True).distinct()
            field_instance = django_filters.MultipleChoiceFilter(
                field_name=field,
                choices=[(choice, choice) for choice in qs.all()],
                widget=forms.SelectMultiple(attrs={"class": "form-control"}),
            )
            self.filters[field] = field_instance

    class Meta:
        model = ScalarData
        fields = [
            "region",
            "input_energy_vector",
            "output_energy_vector",
            "parameter_name",
            "technology",
            "technology_type",
        ]
