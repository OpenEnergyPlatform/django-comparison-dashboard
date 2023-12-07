from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django_htmx.http import retarget

from . import graphs, models, preprocessing, sources
from .filters import FormFilter, GraphOptionForm
from .models import ScalarData


class DashboardView(TemplateView):
    template_name = "django_comparison_dashboard/dashboard.html"


def index(request):
    filter_list = ScalarData.objects.all()
    f = FormFilter(request.GET, queryset=filter_list)
    context = {"filter_form": f}
    return render(request, "django_comparison_dashboard/dashboard.html", context)


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
    filter_form = FormFilter(queryset=scalar_data)
    graph_options_form = GraphOptionForm()
    return render(
        request,
        "django_comparison_dashboard/dashboard.html",
        {"filter_form": filter_form, "graph_options_form": graph_options_form, "scenarios": selected_scenarios},
    )


def scalar_data_plot(request):
    selected_scenarios = request.GET.getlist("scenario_id")
    scalar_data = ScalarData.objects.filter(scenario__in=selected_scenarios)
    filter_form = FormFilter(request.GET, queryset=scalar_data)
    graph_options_form = GraphOptionForm(request.GET)
    if not filter_form.is_valid():
        response = render(
            request,
            "django_comparison_dashboard/dashboard.html#filters",
            {"filter_form": filter_form, "scenarios": selected_scenarios},
        )
        return retarget(response, "#filters")
    df = preprocessing.get_scalar_data(filter_form.qs, [], []).to_dict(orient="records")
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
    filter_form = FormFilter(request.GET, queryset=scalar_data)
    if filter_form.is_valid():
        df = preprocessing.get_scalar_data(filter_form.qs, [], [])
        return HttpResponse(df.to_html())
    else:
        response = render(
            request,
            "django_comparison_dashboard/dashboard.html#filters",
            {"filter_form": filter_form, "scenarios": selected_scenarios},
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
