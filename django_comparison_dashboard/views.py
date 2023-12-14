from django.contrib import messages
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django_htmx.http import retarget

from . import graphs, models, preprocessing, sources
from .filters import ScenarioFilter
from .forms import ColorForm, DataFilterSet, GraphFilterSet, LabelForm
from .models import ScalarData


class DashboardView(TemplateView):
    template_name = "django_comparison_dashboard/dashboard.html"


def index(request):
    filter_list = ScalarData.objects.all()
    scenario_filter = ScenarioFilter(request.GET, queryset=filter_list)
    return render(request, "django_comparison_dashboard/dashboard.html", {"scenario_filter": scenario_filter})


def add_label_form(request):
    label_form = LabelForm()
    return render(
        request,
        "django_comparison_dashboard/dashboard.html#labels",
        {
            "label_form": label_form,
        },
    )


def add_color_form(request):
    color_form = ColorForm()
    return render(
        request,
        "django_comparison_dashboard/dashboard.html#colors",
        {
            "color_form": color_form,
        },
    )


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
    filter_set = DataFilterSet(selected_scenarios)
    graph_filter_set = GraphFilterSet()
    return render(
        request,
        "django_comparison_dashboard/dashboard.html",
        context=filter_set.get_context_data() | graph_filter_set.get_context_data(),
    )


def scalar_data_plot(request):
    selected_scenarios = request.GET.getlist("scenario_id")
    filter_set = DataFilterSet(selected_scenarios, request.GET)
    if not filter_set.is_valid():
        response = render(
            request,
            "django_comparison_dashboard/dashboard.html#filters",
            context=filter_set.get_context_data(),
        )
        return retarget(response, "#filters")
    df = preprocessing.get_scalar_data(filter_set).to_dict(orient="records")

    graph_filter_set = GraphFilterSet(request.GET)
    if not graph_filter_set.is_valid():
        response = render(
            request,
            "django_comparison_dashboard/dashboard.html#graph_options",
            context=graph_filter_set.get_context_data(),
        )
        return retarget(response, "#graph_options")

    # checking if the filters choosen for the x and y Axis are part of the filters chosen in group_by
    # when group_by is [] all values were choose for the dataframe
    if filter_set.group_by:
        if not graph_filter_set.cleaned_data["x"] in filter_set.group_by:
            messages.add_message(
                request, messages.WARNING, "Please choose a value for the X-Axis that was also chosen in Group-By."
            )
        if not graph_filter_set.cleaned_data["y"] in filter_set.group_by:
            messages.add_message(
                request, messages.WARNING, "Please choose a value for the Y-Axis that was also chosen in Group-By."
            )

    return HttpResponse(graphs.bar_plot(df, graph_filter_set).to_html())


def scalar_data_table(request):
    selected_scenarios = request.GET.getlist("scenario_id")
    filter_set = DataFilterSet(selected_scenarios, request.GET)
    if not filter_set.is_valid():
        response = render(
            request,
            "django_comparison_dashboard/dashboard.html#filters",
            context=filter_set.get_context_data(),
        )
        return retarget(response, "#filters")
    df = preprocessing.get_scalar_data(filter_set)
    return HttpResponse(df.to_html())


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
