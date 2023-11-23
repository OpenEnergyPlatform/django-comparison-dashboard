import django_filters
from django import forms

from .models import ScalarData


class FormFilter(django_filters.FilterSet):
    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        for field in ScalarData.filters:
            qs = self.queryset.order_by().values_list(field, flat=True).distinct()
            field_instance = django_filters.MultipleChoiceFilter(
                field_name=field, choices=[(choice, choice) for choice in qs.all()]
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


def available_filters():
    available_filters = [(filter_name, filter_name) for filter_name in ScalarData.filters]
    return available_filters


class GraphOptionForm(forms.Form):
    x = forms.ChoiceField(label="X-Axis", choices=available_filters)
    y = forms.ChoiceField(label="Y-Axis", choices=available_filters)
    text = forms.ChoiceField(label="Text", choices=available_filters)
    color = forms.ChoiceField(label="Color", choices=available_filters)
    hover_name = forms.ChoiceField(label="Hover", choices=available_filters)
    orientation = forms.ChoiceField(label="Orientation", choices=(("v", "vertical"), ("h", "horizontal")))
    barmode = forms.ChoiceField(label="Mode", choices=((0, "relative"), (1, "group"), (2, "overlay")))
    facet_col = forms.ChoiceField(label="Subplots", choices=available_filters)
    facet_col_wrap = forms.IntegerField(label="Subplots per Row")
