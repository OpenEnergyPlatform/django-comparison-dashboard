from django import forms
from django.forms.utils import ErrorDict

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


# left hand side filters for used for data selection


def available_filters():
    # get available filters from FormFilter
    available_filters = []
    for filter_name in ScalarData.filters:
        filter_values = ScalarData.objects.values_list(filter_name, flat=True).distinct()
        if filter_values:
            available_filters.append((filter_name, filter_name))
    return available_filters


def available_filters_empty():
    # get available filters from FormFilter
    available_filters = []
    available_filters.append(("", "---"))
    for filter_name in ScalarData.filters:
        filter_values = ScalarData.objects.values_list(filter_name, flat=True).distinct()
        if filter_values:
            available_filters.append((filter_name, filter_name))
    return available_filters


class OrderAggregationForm(forms.Form):
    order_by = forms.MultipleChoiceField(label="Order-By", choices=available_filters, required=False)
    group_by = forms.MultipleChoiceField(label="Group-By", choices=available_filters, required=False)
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


class LabelForm(forms.Form):
    label_key = forms.CharField(label="name of the thing to be labeled", required=False)
    label_value = forms.CharField(label="new label", required=False)

    def full_clean(self):
        """Pair keys and values into dict"""
        self._errors = ErrorDict()
        self.cleaned_data = dict(zip(self.data.getlist("label_key"), self.data.getlist("label_value")))


class ColorForm(forms.Form):
    color_name = forms.CharField(label="set color for", required=False)
    color_field = forms.CharField(label="color", widget=forms.TextInput(attrs={"type": "color"}), required=False)


# right hand side options for plotting charts


class GraphOptionForm(forms.Form):
    x = forms.ChoiceField(label="X-Axis", choices=available_filters, help_text="help text")
    y = forms.ChoiceField(label="Y-Axis", choices=available_filters)
    text = forms.ChoiceField(label="Text", choices=available_filters_empty, required=False)
    color = forms.ChoiceField(label="Color", choices=available_filters)
    hover_name = forms.ChoiceField(label="Hover", choices=available_filters)
    orientation = forms.ChoiceField(label="Orientation", choices=(("v", "vertical"), ("h", "horizontal")))
    barmode = forms.ChoiceField(
        label="Mode", choices=(("relative", "relative"), ("group", "group"), ("overlay", "overlay"))
    )
    facet_col = forms.ChoiceField(label="Subplots", choices=available_filters_empty, required=False)
    facet_col_wrap = forms.IntegerField(label="Subplots per Row")

    def clean_facet_col(self):
        data = self.cleaned_data["facet_col"]
        if data == "":
            return None
        return data

    def clean_text(self):
        data = self.cleaned_data["text"]
        if data == "":
            return None
        return data


class DisplayOptionForm(forms.Form):
    chart_height = forms.IntegerField(label="Chart Height", required=False)
    x_title = forms.CharField(label="X-Axis Title", required=False)
    y_title = forms.CharField(label="Y-Axis Title", required=False)
    subplot_title = forms.CharField(label="Subplot Title", required=False)
    show_legend = forms.BooleanField(label="Show Legend", required=False)
    legend_title = forms.CharField(label="Legend Title", required=False)
    bar_gap = forms.IntegerField(label="Bar Gap", required=False)
    margin_left = forms.IntegerField(label="Margin Left", required=False)
    margin_right = forms.IntegerField(label="Margin Right", required=False)
    margin_top = forms.IntegerField(label="Margin Top", required=False)
    margin_bottom = forms.IntegerField(label="Margin Bottom", required=False)
    subplot_spacing = forms.IntegerField(label="Subplot Spacing", required=False)
