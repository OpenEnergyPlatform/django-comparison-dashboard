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
    # get available filters from FormFilter
    available_filters = []
    for filter_name in ScalarData.filters:
        filter_values = ScalarData.objects.values_list(filter_name, flat=True).distinct()
        if filter_values:
            available_filters.append((filter_name, filter_name))
    return available_filters


class GraphOptionForm(forms.Form):
    x = forms.ChoiceField(label="X-Axis", choices=available_filters)
    # field help_text packt den Text direkt neben das Feld, bräuchte etwas htmx Umweg oder
    # bootstrap magic um gut auszusehen
    y = forms.ChoiceField(label="Y-Axis", choices=available_filters)
    text = forms.ChoiceField(label="Text", choices=available_filters)
    color = forms.ChoiceField(label="Color", choices=available_filters)
    hover_name = forms.ChoiceField(label="Hover", choices=available_filters)
    orientation = forms.ChoiceField(label="Orientation", choices=(("v", "vertical"), ("h", "horizontal")))
    barmode = forms.ChoiceField(
        label="Mode", choices=(("relative", "relative"), ("group", "group"), ("overlay", "overlay"))
    )
    facet_col = forms.ChoiceField(label="Subplots", choices=((None, "Nothing"), ("region", "region")), required=False)
    # wird als leer übergeben in der query und wirft preprozessing error
    facet_col_wrap = forms.IntegerField(label="Subplots per Row")


class OrderAggregationForm(forms.Form):
    # wird for some reason nicht angezeigt ?? Obwohl in views und dashboard.html eingebunden
    order_by = forms.ChoiceField(label="Order-By", choices=available_filters)
    group_by = forms.ChoiceField(label="Group-By", choices=available_filters)
    normalize = forms.BooleanField(label="Normalize Data", required=False)


class UnitForm(forms.Form):
    energy = forms.ChoiceField(
        label="Energy", initial="GWh", choices=(("kWh", "kWh"), ("MWh", "MWh"), ("GWh", "GWh"), ("TWh", "TWh"))
    )
    power = forms.ChoiceField(
        label="Power", initial="GW", choices=(("kW", "kW"), ("MW", "MW"), ("GW", "GW"), ("TW", "TW"))
    )
    power_per_hour = forms.ChoiceField(
        label="Power per Hour",
        initial="MW/h",
        choices=(("kW/h", "kW/h"), ("MW/h", "MW/h"), ("GW/h", "GW/h"), ("TW/h", "TW/h")),
    )
    mass = forms.ChoiceField(label="Mass", initial="Gt", choices=(("Mt", "Mt"), ("Gt", "Gt")))
    mass_per_year = forms.ChoiceField(
        label="Mass per year", initial="Gt/a", choices=(("Mt/a", "Mt/a"), ("Gt/a", "Gt/a"))
    )
