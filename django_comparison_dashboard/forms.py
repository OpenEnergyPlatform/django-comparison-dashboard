from django import forms

from . import settings
from .models import ScalarData


class Scenario(forms.Form):
    scenarios = forms.MultipleChoiceField(
        choices=[
            ("code_exposed_fig1", "code_exposed_fig1"),
            ("base_latest", "base_latest"),
            ("dummy_save", "dummy_save"),
            ("ID1,2_paper", "ID1,2_paper"),
        ]
    )


class Filter(forms.Form):
    tags = forms.ChoiceField(label="Filter Tags")
    year = forms.ChoiceField(label="Filter Year")
    region = forms.ChoiceField(label="Filter Region")

    def __init__(self, *args, **kwargs):
        options = kwargs.pop("options", None)
        super().__init__(*args, **kwargs)
        if options:
            for filter, choice_list in options.items():
                self.fields[filter].choices = choice_list


class DataSourceUploadForm(forms.Form):
    """Default upload form for a data source"""

    scenario_id = forms.CharField(max_length=255)
    data_type = forms.ChoiceField(choices=[(dt.name, dt.name) for dt in settings.DataType])


class CSVSourceUploadForm(DataSourceUploadForm):
    """Upload form for CSV data source"""

    csv_file = forms.FileField()


def available_filters():
    # get available filters from FormFilter
    available_filters = []
    for filter_name in ScalarData.filters:
        filter_values = ScalarData.objects.values_list(filter_name, flat=True).distinct()
        if filter_values:
            available_filters.append((filter_name, filter_name))
    return available_filters


class GraphOptionForm(forms.Form):
    x = forms.ChoiceField(label="X-Axis", choices=available_filters, help_text="help text")
    y = forms.ChoiceField(label="Y-Axis", choices=available_filters)
    text = forms.ChoiceField(label="Text", choices=available_filters)
    color = forms.ChoiceField(label="Color", choices=available_filters)
    hover_name = forms.ChoiceField(label="Hover", choices=available_filters)
    orientation = forms.ChoiceField(label="Orientation", choices=(("v", "vertical"), ("h", "horizontal")))
    barmode = forms.ChoiceField(
        label="Mode", choices=(("relative", "relative"), ("group", "group"), ("overlay", "overlay"))
    )
    facet_col = forms.ChoiceField(label="Subplots", choices=((None, "Nothing"), ("region", "region")), required=False)
    facet_col_wrap = forms.IntegerField(label="Subplots per Row")


class OrderAggregationForm(forms.Form):
    order_by = forms.MultipleChoiceField(label="Order-By", choices=available_filters)
    group_by = forms.MultipleChoiceField(label="Group-By", choices=available_filters)
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
