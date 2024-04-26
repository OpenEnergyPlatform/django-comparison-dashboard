from django.forms.formsets import formset_factory
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import DetailView, FormView, ListView, TemplateView, View
from django_htmx.http import retarget

from . import graphs, models, preprocessing, sources
from .filters import ScenarioFilter
from .forms import BarGraphFilterSet, ChartTypeForm, DataFilterSet, SankeyGraphFilterSet  # noqa: F401
from .models import FilterSettings, ScalarData


class DashboardView(TemplateView):
    template_name = "django_comparison_dashboard/dashboard.html"


def index(request):
    filter_list = ScalarData.objects.all()
    scenario_filter = ScenarioFilter(request.GET, queryset=filter_list)
    return render(request, "django_comparison_dashboard/dashboard.html", {"scenario_filter": scenario_filter})


class KeyValueFormPartialView(View):
    prefix = ""
    form = None

    def __init__(self, prefix, form, **kwargs):
        super().__init__(**kwargs)
        self.prefix = prefix
        self.form = form

    def post(self, request):
        count = int(request.POST[f"{self.prefix}-TOTAL_FORMS"])
        form_data = request.POST.dict()
        if "add" in request.path:
            form_data[f"{self.prefix}-TOTAL_FORMS"] = count + 1
        if "remove" in request.path:
            if count > 0:
                form_data[f"{self.prefix}-TOTAL_FORMS"] = count - 1
        formset = formset_factory(self.form)
        form = formset(form_data, prefix=self.prefix)
        return HttpResponse(form.as_p())


def get_filters(request):
    """
    sets up the diffrent Forms/FilterSets for the dashboard
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
    graph_filter_set = BarGraphFilterSet()
    chart_type_form = ChartTypeForm()
    return render(
        request,
        "django_comparison_dashboard/dashboard.html",
        context=filter_set.get_context_data()
        | graph_filter_set.get_context_data()
        | {"name_list": filter_setting_names, "chart_type_form": chart_type_form},
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

        selected_chart_type = request.GET.get("chart_type")
        selected_chart = graphs.CHART_DATA.get(selected_chart_type)
        form_class = selected_chart["form_class"]
        graph_filter_set = form_class(self.request.GET, data_filter_set=filter_set)
        if not graph_filter_set.is_valid():
            response = render(
                self.request,
                "django_comparison_dashboard/dashboard.html#graph_options",
                context=graph_filter_set.get_context_data(),
            )
            return retarget(response, "#graph_options")
        create_chart = selected_chart["chart_function"]
        return render(request, self.template_name, {"chart": create_chart(df, graph_filter_set).to_html()})


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
    if name == "":
        return HttpResponse("Please enter a name.")
    if FilterSettings.objects.filter(name=name).exists():
        return HttpResponse("Name already exists.")

    selected_scenarios = request.POST.getlist("scenario_id")
    filter_set = DataFilterSet(selected_scenarios, request.POST)
    if not filter_set.is_valid():
        return HttpResponse("Scenario or Other Form not valid.")

    graph_filter_set = BarGraphFilterSet(request.POST, data_filter_set=filter_set)
    if not graph_filter_set.is_valid():
        return HttpResponse("Graph or Display Form not valid.")

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
        return HttpResponse("Please enter a name.", status=400)
    if FilterSettings.objects.filter(name=name).exists():
        return HttpResponse("This name already exits.", status=400)
    else:
        return HttpResponse("Your input is correct.", status=200)


def load_filter_settings(request):
    selected_scenarios = request.GET.getlist("scenario_id")
    name = request.GET.get("name")
    try:
        # need to check the name and if it is in the database
        filter_settings = FilterSettings.objects.get(name=name)

        filter_set = DataFilterSet(selected_scenarios, filter_settings.filter_set)
        graph_filter_set = BarGraphFilterSet(filter_settings.graph_filter_set, filter_set)
        filter_setting_names = list(FilterSettings.objects.values("name"))

        return render(
            request,
            "django_comparison_dashboard/dashboard.html",
            context=filter_set.get_context_data()
            | graph_filter_set.get_context_data()
            | {"name_list": filter_setting_names},
        )
    except FilterSettings.DoesNotExist:
        # needs a proper error
        return HttpResponse(status=404)


def refresh_graph_filter_set(request):
    """
    called when type of chart is changed and refreshes the correponding graph and display options.
    """
    if request.method == "POST":
        selected_option = request.POST.get("chart_type")
        selected_chart = graphs.CHART_DATA.get(selected_option)
        filter_set_class = selected_chart["form_class"]
        graph_filter_set = filter_set_class()

    template_partials = [
        "django_comparison_dashboard/dashboard.html#graph_options",
        "django_comparison_dashboard/dashboard.html#display_options",
    ]
    context = graph_filter_set.get_context_data() | {"chart_type_form": ChartTypeForm(request.POST)}
    response = HttpResponse(render_to_string(template_name, context) for template_name in template_partials)
    return response


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

    selected_chart_type = request.GET.get("chart_type")
    selected_chart = graphs.CHART_DATA.get(selected_chart_type)
    form_class = selected_chart["form_class"]
    graph_filter_set = form_class(request.GET, data_filter_set=filter_set)
    if not graph_filter_set.is_valid():
        error_type = "graph options"
        return HttpResponseBadRequest(error_message.format(error_type=error_type))
    df = preprocessing.get_scalar_data(filter_set).to_dict(orient="records")
    create_chart = selected_chart["chart_function"]
    response = HttpResponse(create_chart(df, graph_filter_set).to_html())
    response["HX-Redirect"] = request.get_full_path_info()
    return response


class ScenarioSelectionView(ListView):
    template_name = "django_comparison_dashboard/scenario_list.html"
    extra_context = {"sources": models.Source.objects.order_by("name").all()}
    context_object_name = "scenarios"

    def get_queryset(self):
        if "source" in self.request.GET:
            source = self.request.GET["source"]
            return models.Result.objects.filter(source=source)
        else:
            return models.Result.objects.filter(source=models.Source.objects.order_by("name").first())

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
        return models.Result.objects.get(pk=scenario_id)


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
        if models.Result.objects.filter(source__name=source.name, name=scenario.id).exists():
            return HttpResponse("Scenario already present in database.")
        scenario.download()
        return HttpResponse(f"Uploaded scenario '{scenario}'.")
