from django import forms
from django.forms.formsets import BaseFormSet, formset_factory

from . import settings
from .filters import ScenarioFilter
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


def get_available_filters(value=False, empty=False):
    available_filters = [(filter_name, filter_name) for filter_name in ScalarData.filters]
    if value:
        available_filters.insert(0, ("value", "value"))
    if empty:
        available_filters.insert(0, ("", "---"))
    return available_filters


class OrderAggregationForm(forms.Form):
    order_by = forms.MultipleChoiceField(
        label="Order-By",
        choices=get_available_filters,
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )
    group_by = forms.MultipleChoiceField(
        label="Group-By",
        choices=get_available_filters,
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )
    normalize = forms.BooleanField(
        label="Normalize Data", required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )


class UnitForm(forms.Form):
    energy = forms.ChoiceField(
        label="Energy",
        initial="GWh",
        choices=(("kWh", "kWh"), ("MWh", "MWh"), ("GWh", "GWh"), ("TWh", "TWh")),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    power = forms.ChoiceField(
        label="Power",
        initial="GW",
        choices=(("kW", "kW"), ("MW", "MW"), ("GW", "GW"), ("TW", "TW")),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    power_per_hour = forms.ChoiceField(
        label="Power per Hour",
        initial="MW/h",
        choices=(("kW/h", "kW/h"), ("MW/h", "MW/h"), ("GW/h", "GW/h"), ("TW/h", "TW/h")),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    mass = forms.ChoiceField(
        label="Mass",
        initial="Gt",
        choices=(("Mt", "Mt"), ("Gt", "Gt")),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    mass_per_year = forms.ChoiceField(
        label="Mass per year",
        initial="Gt/a",
        choices=(("Mt/a", "Mt/a"), ("Gt/a", "Gt/a")),
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class LabelForm(forms.Form):
    label_key = forms.CharField(
        label="name of the thing to be labeled",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    label_value = forms.CharField(
        label="new label", required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )


class KeyValueFormset(BaseFormSet):
    def __init__(self, data=None, **kwargs):
        super().__init__(data, **kwargs)
        if data is not None and isinstance(data, dict) and self.key_field_name in data:
            item_count = len(data[self.key_field_name])
            formset_data = {f"{self.prefix}-INITIAL_FORMS": 0, f"{self.prefix}-TOTAL_FORMS": item_count}
            for i in range(item_count):
                formset_data[f"{self.prefix}-{i}-{self.key_field_name}"] = data[self.key_field_name][i]
                formset_data[f"{self.prefix}-{i}-{self.value_field_name}"] = data[self.value_field_name][i]
            self.data = formset_data

    @property
    def key_field_name(self):
        return next(field for field in self.form.base_fields.keys() if field.endswith("_key"))

    @property
    def value_field_name(self):
        return next(field for field in self.form.base_fields.keys() if field.endswith("_value"))

    @property
    def cleaned_data(self):
        """Pair keys and values into dict"""
        cleaned_data_raw = super().cleaned_data
        return {
            self.key_field_name: [entry[self.key_field_name] for entry in cleaned_data_raw if entry],
            self.value_field_name: [entry[self.value_field_name] for entry in cleaned_data_raw if entry],
        }


class ColorForm(forms.Form):
    color_key = forms.CharField(
        label="set color for", required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    color_value = forms.CharField(label="color", widget=forms.TextInput(attrs={"type": "color"}), required=False)


class GraphOptionForm(forms.Form):
    x = forms.ChoiceField(
        label="X-Axis",
        choices=get_available_filters(value=True),
        # help_text="<span class='helptext' data-toggle='tooltip'
        # data-placement='top' title='tooltip content'>?</span>",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    y = forms.ChoiceField(
        label="Y-Axis", choices=get_available_filters(value=True), widget=forms.Select(attrs={"class": "form-control"})
    )
    text = forms.ChoiceField(
        label="Text",
        choices=get_available_filters(value=True, empty=True),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    color = forms.ChoiceField(
        label="Color", choices=get_available_filters, widget=forms.Select(attrs={"class": "form-control"})
    )
    hover_name = forms.ChoiceField(
        label="Hover", choices=get_available_filters, widget=forms.Select(attrs={"class": "form-control"})
    )
    orientation = forms.ChoiceField(
        label="Orientation",
        choices=(("v", "vertical"), ("h", "horizontal")),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    barmode = forms.ChoiceField(
        label="Mode",
        choices=(("relative", "relative"), ("group", "group"), ("overlay", "overlay")),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    facet_col = forms.ChoiceField(
        label="Subplots",
        choices=get_available_filters(empty=True),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    facet_col_wrap = forms.IntegerField(
        label="Subplots per Row", widget=forms.NumberInput(attrs={"class": "form-control"}), initial=1
    )

    def __init__(self, *args, **kwargs):
        self.data_filter_set = kwargs.pop("data_filter_set", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        for key in ("x", "y", "color", "hover_name"):
            value = cleaned_data[key]
            if (
                self.data_filter_set
                and self.data_filter_set.group_by
                and value not in self.data_filter_set.group_by + ["value"]
            ):
                self.add_error(key, "Please choose a value that was also chosen in Group-By.")
        return cleaned_data

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


class SankeyGraphForm(forms.Form):
    input = forms.ChoiceField(
        label="Input",
        choices=get_available_filters(value=True),
        # help_text="<span class='helptext' data-toggle='tooltip'
        # data-placement='top' title='tooltip content'>?</span>",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    output = forms.ChoiceField(
        label="Output", choices=get_available_filters(value=True), widget=forms.Select(attrs={"class": "form-control"})
    )
    process = forms.ChoiceField(
        label="process",
        choices=get_available_filters(value=True),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    font_size = forms.IntegerField(
        label="Font Size", required=False, widget=forms.NumberInput(attrs={"class": "form-control"}), initial=10
    )
    title_text = forms.CharField(
        label="Title", required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )

    def __init__(self, *args, **kwargs):
        self.data_filter_set = kwargs.pop("data_filter_set", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        for key in ("input", "output"):
            value = cleaned_data[key]
            if (
                self.data_filter_set
                and self.data_filter_set.group_by
                and value not in self.data_filter_set.group_by + ["value"]
            ):
                self.add_error(key, "Please choose a value that was also chosen in Group-By.")
        return cleaned_data

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
    chart_height = forms.IntegerField(
        label="Chart Height", required=False, widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    x_title = forms.CharField(
        label="X-Axis Title", required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    y_title = forms.CharField(
        label="Y-Axis Title", required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    subplot_title = forms.CharField(
        label="Subplot Title", required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    show_legend = forms.BooleanField(
        label="Show Legend", required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )
    legend_title = forms.CharField(
        label="Legend Title", required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    bar_gap = forms.IntegerField(
        label="Bar Gap", required=False, widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    margin_left = forms.IntegerField(
        label="Margin Left", required=False, widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    margin_right = forms.IntegerField(
        label="Margin Right", required=False, widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    margin_top = forms.IntegerField(
        label="Margin Top", required=False, widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    margin_bottom = forms.IntegerField(
        label="Margin Bottom", required=False, widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    subplot_spacing = forms.IntegerField(
        label="Subplot Spacing", required=False, widget=forms.NumberInput(attrs={"class": "form-control"})
    )


class SankeyDisplayForm(forms.Form):
    font_size = forms.IntegerField(
        label="Font Size", required=False, widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    title_text = forms.CharField(
        label="Title", required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )


class FilterSet:
    forms = {}

    def __init__(self, data: dict | None = None):
        self.bound_forms = {form_name: form(data) for form_name, form in self.forms.items()}

    def is_valid(self) -> bool:
        for form in self.get_forms().values():
            if not form.is_valid():
                return False
        return True

    def get_forms(self) -> dict[str, "forms.Form"]:
        return self.bound_forms

    def get_context_data(self) -> dict:
        return self.get_forms()

    @property
    def cleaned_data(self) -> dict:
        data = {}
        for form in self.bound_forms.values():
            if isinstance(form, ScenarioFilter):
                data |= form.form.cleaned_data
                continue
            data |= form.cleaned_data
        return data


class DataFilterSet(FilterSet):
    forms = {
        "order_aggregation_form": OrderAggregationForm,
        "unit_form": UnitForm,
    }

    def __init__(self, selected_scenarios: list[int], data: dict | None = None):
        """Get filter set from selected scenarios."""
        super().__init__(data)
        self.selected_scenarios = selected_scenarios
        scalar_data = ScalarData.objects.filter(result__in=selected_scenarios)
        self.bound_forms["scenario_filter"] = ScenarioFilter(data, queryset=scalar_data)
        self.bound_forms["label_form"] = formset_factory(LabelForm, KeyValueFormset)(data, prefix="labels")

    @property
    def queryset(self):
        return self.bound_forms["scenario_filter"].qs

    @property
    def order_by(self):
        return self.bound_forms["order_aggregation_form"].cleaned_data["order_by"]

    @property
    def group_by(self):
        return self.bound_forms["order_aggregation_form"].cleaned_data["group_by"]

    @property
    def units(self):
        return self.bound_forms["unit_form"].cleaned_data.values()

    @property
    def labels(self):
        labels_raw = self.bound_forms["label_form"].cleaned_data
        return {key: value for key, value in zip(labels_raw["label_key"], labels_raw["label_value"])}

    def get_context_data(self):
        context = super().get_context_data()
        context["scenarios"] = self.selected_scenarios
        return context

    def get_forms(self) -> dict[str, "forms.Form"]:
        return self.bound_forms


class BarGraphFilterSet(FilterSet):
    forms = {
        "display_options_form": DisplayOptionForm,
    }

    def __init__(self, data: dict | None = None, data_filter_set: DataFilterSet | None = None):
        super().__init__(data)
        self.bound_forms["graph_options_form"] = GraphOptionForm(data, data_filter_set=data_filter_set)
        self.bound_forms["color_form"] = formset_factory(ColorForm, KeyValueFormset)(data, prefix="colors")

    @property
    def plot_options(self):
        if self.bound_forms["graph_options_form"].is_valid():
            options = self.bound_forms["graph_options_form"].cleaned_data
        colors_raw = self.bound_forms["color_form"].cleaned_data
        options["color_discrete_map"] = {
            key: value for key, value in zip(colors_raw["color_key"], colors_raw["color_value"])
        }
        return options

    def get_forms(self) -> dict[str, "forms.Form"]:
        return self.bound_forms


class SankeyGraphFilterSet(FilterSet):
    forms = {
        "display_options_form": SankeyDisplayForm,
    }

    def __init__(self, data: dict | None = None, data_filter_set: DataFilterSet | None = None):
        super().__init__(data)
        self.bound_forms["graph_options_form"] = SankeyGraphForm(data, data_filter_set=data_filter_set)
        self.bound_forms["color_form"] = formset_factory(ColorForm, KeyValueFormset)(data, prefix="colors")

    @property
    def plot_options(self):
        if self.bound_forms["graph_options_form"].is_valid():
            options = self.bound_forms["graph_options_form"].cleaned_data
        colors_raw = self.bound_forms["color_form"].cleaned_data
        options["color_discrete_map"] = {
            key: value for key, value in zip(colors_raw["color_key"], colors_raw["color_value"])
        }
        return options

    def get_forms(self) -> dict[str, "forms.Form"]:
        return self.bound_forms
