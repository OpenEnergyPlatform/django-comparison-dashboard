from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django_htmx.http import retarget

from . import graphs, models, preprocessing, sources
from .filters import ScenarioFilter
from .forms import GraphOptionForm, OrderAggregationForm, UnitForm
from .models import ScalarData


class IndexView(TemplateView):
    template_name = "django_comparison_dashboard/index.html"


class DashboardView(TemplateView):
    template_name = "django_comparison_dashboard/dashboard.html"


def index(request):
    filter_list = ScalarData.objects.all()
    scenario_filter = ScenarioFilter(request.GET, queryset=filter_list)
    return render(request, "django_comparison_dashboard/dashboard.html", {"scenario_filter": scenario_filter})


def get_filters(request):
    """

    Example for incoming request: localhost:8000/dashboard/?scenario_id=5&scenario_id=10

    Parameters
    ----------
    request

    Returns
    -------

    """
    selected_scenarios = request.GET.getlist("scenario_id")
    scalar_data = ScalarData.objects.filter(scenario__in=selected_scenarios)
    scenario_filter = ScenarioFilter(queryset=scalar_data)
    graph_options_form = GraphOptionForm()
    order_aggregation_form = OrderAggregationForm()
    unit_form = UnitForm()
    return render(
        request,
        "django_comparison_dashboard/dashboard.html",
        {
            "scenario_filter": scenario_filter,
            "graph_options_form": graph_options_form,
            "scenarios": selected_scenarios,
            "order_aggregation_form": order_aggregation_form,
            "unit_form": unit_form,
        },
    )


def scalar_data_plot(request):
    selected_scenarios = request.GET.getlist("scenario_id")
    scalar_data = ScalarData.objects.filter(scenario__in=selected_scenarios)
    scenario_filter = ScenarioFilter(request.GET, queryset=scalar_data)
    order_aggregation_form = OrderAggregationForm(request.GET)
    unit_form = UnitForm(request.GET)
    graph_options_form = GraphOptionForm(request.GET)
    if not scenario_filter.is_valid():
        response = render(
            request,
            "django_comparison_dashboard/dashboard.html#filters",
            {
                "scenario_filter": scenario_filter,
                "scenarios": selected_scenarios,
                "order_aggregation_form": order_aggregation_form,
                "unit_form": unit_form,
            },
        )
        return retarget(response, "#filters")
    if not order_aggregation_form.is_valid():
        response = render(
            request,
            "django_comparison_dashboard/dashboard.html#filters",
            {
                "scenario_filter": scenario_filter,
                "scenarios": selected_scenarios,
                "order_aggregation_form": order_aggregation_form,
                "unit_form": unit_form,
            },
        )
        return retarget(response, "#filters")
    if not unit_form.is_valid():
        response = render(
            request,
            "django_comparison_dashboard/dashboard.html#filters",
            {
                "scenario_filter": scenario_filter,
                "scenarios": selected_scenarios,
                "order_aggregation_form": order_aggregation_form,
                "unit_form": unit_form,
            },
        )
        return retarget(response, "#filters")
    df = preprocessing.get_scalar_data(scenario_filter.qs, [], unit_form.cleaned_data).to_dict(orient="records")
    if not graph_options_form.is_valid():
        response = render(
            request,
            "django_comparison_dashboard/dashboard.html#graph_options",
            {"graph_options_form": graph_options_form},
        )
        return retarget(response, "#graph_options")

    return HttpResponse(graphs.bar_plot(df, graph_options_form.cleaned_data).to_html())


def scalar_data_table(request):
    selected_scenarios = request.GET.getlist("scenario_id")
    scalar_data = ScalarData.objects.filter(scenario__in=selected_scenarios)
    scenario_filter = ScenarioFilter(request.GET, queryset=scalar_data)
    if scenario_filter.is_valid():
        df = preprocessing.get_scalar_data(scenario_filter.qs, [], [])
        return HttpResponse(df.to_html())
    else:
        response = render(
            request,
            "django_comparison_dashboard/dashboard.html#filters",
            {"scenario_filter": scenario_filter, "scenarios": selected_scenarios},
        )
        return retarget(response, "#filters")


class ScenarioSelectionView(ListView):
    template_name = "django_comparison_dashboard/scenario_list.html"
    extra_context = {"sources": models.Source.objects.order_by("name").all()}
    context_object_name = "scenarios"

    def get_queryset(self):
        if "source" in self.request.GET:
            source = self.request.GET["source"]
            return models.Scenario.objects.filter(source=source)
        else:
            return models.Scenario.objects.filter(source=models.Source.objects.order_by("name").first())

    def get_template_names(self):
        if "source" in self.request.GET:
            return [f"{self.template_name}#scenarios"]
        else:
            return super().get_template_names()


class ScenarioDetailView(DetailView):
    template_name = "django_comparison_dashboard/scenario_list.html#scenario"
    context_object_name = "scenario"

    def get_object(self, queryset=None):
        scenario_id = self.request.GET["scenario"]
        return models.Scenario.objects.get(pk=scenario_id)


class UploadView(TemplateView):
    template_name = "django_comparison_dashboard/upload_data.html"

    def get_context_data(self, **kwargs):
        return {"sources": sources.SOURCES.sources}


class ScenarioFormView(FormView):
    template_name = "django_comparison_dashboard/upload_data.html#scenario"

    def get_source(self):
        source_name = self.request.GET["source"] if self.request.method == "GET" else self.request.POST["source"]
        source: sources.DataSource = sources.SOURCES[source_name]
        return source

    def get_form_class(self):
        return self.get_source().form

    def form_valid(self, form):
        source = self.get_source()
        scenario = source.scenario(**form.cleaned_data)
        if models.Scenario.objects.filter(source__name=source.name, name=scenario.id).exists():
            return HttpResponse("Scenario already present in database.")
        scenario.download()
        return HttpResponse(f"Uploaded scenario '{scenario}'.")
