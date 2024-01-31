from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django_htmx.http import retarget

from . import graphs, models, preprocessing, sources
from .filters import ScenarioFilter
from .forms import ColorForm, DataFilterSet, GraphFilterSet, LabelForm
from .models import FilterSettings, ScalarData


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
    filter_setting_names = list(FilterSettings.objects.values("name"))
    filter_set = DataFilterSet(selected_scenarios)
    graph_filter_set = GraphFilterSet()
    return render(
        request,
        "django_comparison_dashboard/dashboard.html",
        context=filter_set.get_context_data()
        | graph_filter_set.get_context_data()
        | {"name_list": filter_setting_names},
    )


class ScalarPlotView(TemplateView):
    template_name = "django_comparison_dashboard/partials/plot.html"

    def get(self, request, *args, **kwargs):
        selected_scenarios = self.request.GET.getlist("scenario_id")
        filter_set = DataFilterSet(selected_scenarios, self.request.GET)
        if not filter_set.is_valid():
            response = render(
                self.request,
                "django_comparison_dashboard/dashboard.html#filters",
                context=filter_set.get_context_data(),
            )
            return retarget(response, "#filters")
        df = preprocessing.get_scalar_data(filter_set).to_dict(orient="records")

        graph_filter_set = GraphFilterSet(self.request.GET, data_filter_set=filter_set)
        if not graph_filter_set.is_valid():
            response = render(
                self.request,
                "django_comparison_dashboard/dashboard.html#graph_options",
                context=graph_filter_set.get_context_data(),
            )
            return retarget(response, "#graph_options")

        return render(request, self.template_name, {"chart": graphs.bar_plot(df, graph_filter_set).to_html()})


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


def save_filter_settings(request):
    name = request.POST.get("name")
    name_list = list(FilterSettings.objects.values("name"))
    if name == "" or FilterSettings.objects.filter(name=name).exists():
        response = HttpResponse("<div id='name_error' class='alert alert-warning'>Wrong name input</div>")
        return retarget(response, "#name_error")

    selected_scenarios = request.POST.getlist("scenario_id")
    filter_set = DataFilterSet(selected_scenarios, request.POST)
    if not filter_set.is_valid():
        return HttpResponse(
            "<div id='validation_error' class='alert alert-warning'>Scenario or Other Form not valid</div>"
        )

    graph_filter_set = GraphFilterSet(request.POST, data_filter_set=filter_set)
    if not graph_filter_set.is_valid():
        return HttpResponse(
            "<div id='validation_error' class='alert alert-warning'>Graph or Display Form not valid</div>"
        )

    else:
        # Create an instance of FilterSettings and assign the form data
        filter_settings = FilterSettings(
            name=name,
            filter_set=filter_set.cleaned_data,
            graph_filter_set=graph_filter_set.cleaned_data,
        )
        filter_settings.save()

        response = render(
            request,
            "django_comparison_dashboard/dashboard.html#load_settings",
            {"name_list": name_list},
        )
        return retarget(response, "#load_settings")


def save_precheck_name(request):
    name = request.POST.get("name")
    if name == "":
        return HttpResponse("<div id='name_error' class='alert alert-warning'>Please enter a name.</div>")
    if FilterSettings.objects.filter(name=name).exists():
        return HttpResponse("<div id='name_error' class='alert alert-warning'>This name already exists.</div>")
    else:
        return HttpResponse("<div id='name_error' class='alert alert-success'>Name is valid.</div>")


def load_filter_settings(request):
    selected_scenarios = request.GET.getlist("scenario_id")
    name = request.GET.get("name")
    try:
        # need to check the name and if it is in the database
        filter_settings = FilterSettings.objects.get(name=name)

        filter_set = DataFilterSet(selected_scenarios, filter_settings.filter_set)
        graph_filter_set = GraphFilterSet(filter_settings.graph_filter_set, filter_set)

        return render(
            request,
            "django_comparison_dashboard/dashboard.html",
            context=filter_set.get_context_data() | graph_filter_set.get_context_data(),
        )
    except FilterSettings.DoesNotExist:
        # needs a proper error
        return HttpResponse(status=404)


def get_chart(request):
    # TODO: Merge view ScalarPlotView, check if "single" chart is requested
    selected_scenarios = request.GET.getlist("scenario_id")
    filter_set = DataFilterSet(selected_scenarios, request.GET)
    error_message = (
        "Could not render chart due to invalid {error_type}. "
        "This might occur, if {error_type} have been updated/changed. "
        "Please check {error_type} or regenerate chart URL from "
        "dashboard."
    )
    if not filter_set.is_valid():
        error_type = "filter settings"
        return HttpResponseBadRequest(error_message.format(error_type=error_type))
    graph_filter_set = GraphFilterSet(request.GET, data_filter_set=filter_set)
    if not graph_filter_set.is_valid():
        error_type = "graph options"
        return HttpResponseBadRequest(error_message.format(error_type=error_type))
    df = preprocessing.get_scalar_data(filter_set).to_dict(orient="records")
    response = HttpResponse(graphs.bar_plot(df, graph_filter_set).to_html())
    response["HX-Redirect"] = request.get_full_path_info()
    return response


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
