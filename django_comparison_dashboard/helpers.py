from django_comparison_dashboard import graphs
from django_comparison_dashboard.forms import DataFilterSet
from django_comparison_dashboard.models import FilterSettings, NamedFilterSettings


def save_filters(data, name: str | None = None):
    selected_scenarios = data.getlist("scenario_id")
    selected_chart_type = data.get("chart_type")
    filter_set = DataFilterSet(selected_scenarios, selected_chart_type, data)
    if not filter_set.is_valid():
        raise ValueError("Invalid filter data")

    selected_chart = graphs.CHART_DATA.get(selected_chart_type)
    form_class = selected_chart["form_class"]
    graph_filter_set = form_class(data, data_filter_set=filter_set)
    if not graph_filter_set.is_valid():
        raise ValueError("Invalid graph data")

    # Create an instance of FilterSettings and assign the form data
    graph_filters = graph_filter_set.cleaned_data
    graph_filters["chart_type"] = selected_chart_type
    filter_settings = FilterSettings(filter_set=filter_set.cleaned_data, graph_filter_set=graph_filters)
    filter_settings.save()
    if name:
        named_filter_settings = NamedFilterSettings(name=name, filter_settings=filter_settings)
        named_filter_settings.save()
        return named_filter_settings.id
    return filter_settings.id
