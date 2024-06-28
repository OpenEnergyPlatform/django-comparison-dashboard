from django.forms.formsets import formset_factory
from django.http.response import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import DetailView, FormView, ListView, TemplateView, View
from django_htmx.http import retarget

from . import graphs, models, preprocessing, sources
from .filters import ScenarioFilter
from .forms import BarGraphFilterSet, ChartTypeForm, DataFilterSet, SankeyGraphFilterSet  # noqa: F401
from .models import FilterSettings, NamedFilterSettings, ScalarData


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
    filter_setting_names = list(NamedFilterSettings.objects.values("name"))
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


class ScalarView(TemplateView):
    template_name = "django_comparison_dashboard/partials/plot.html"
    embedded = False

    def get(self, request, *args, **kwargs):
        selected_scenarios = self.request.GET.getlist("scenario_id")

        if "parameters_id" in request.GET:
            # Get form parameters from DB
            parameters = models.FilterSettings.objects.get(pk=request.GET["parameters_id"])
            filter_parameters = parameters.filter_set
            selected_chart_type = parameters.graph_filter_set.pop("chart_type")
            graph_parameters = parameters.graph_filter_set
        else:
            # Get form parameters from request as usual
            filter_parameters = request.GET
            selected_chart_type = request.GET.get("chart_type")
            graph_parameters = request.GET

        filter_set = DataFilterSet(selected_scenarios, filter_parameters)
        if not filter_set.is_valid():
            response = render(
                self.request,
                "django_comparison_dashboard/dashboard.html#filters",
                context=filter_set.get_context_data(),
            )
            return retarget(response, "#filters")
        df = preprocessing.get_scalar_data(filter_set)

        selected_chart = graphs.CHART_DATA.get(selected_chart_type)
        form_class = selected_chart["form_class"]
        graph_filter_set = form_class(graph_parameters, data_filter_set=filter_set)
        if not graph_filter_set.is_valid():
            response = render(
                self.request,
                "django_comparison_dashboard/dashboard.html#graph_options",
                context=graph_filter_set.get_context_data(),
            )
            return retarget(response, "#graph_options")
        chart_function = selected_chart["chart_function"]
        chart = chart_function(df, graph_filter_set).to_html()

        # Check if chart shall be returned in embedded mode
        if "parameters_id" not in request.GET:
            # Store parameters in DB and change query to include "parameters_id" instead of parameter query
            graph_parameters = graph_filter_set.cleaned_data
            graph_parameters["chart_type"] = selected_chart_type
            filter_settings = models.FilterSettings(
                filter_set=filter_set.cleaned_data, graph_filter_set=graph_parameters
            )
            filter_settings.save()
            parameter_id = filter_settings.id
        else:
            parameter_id = request.GET["parameters_id"]
        url = (
            f"{request.path}?"
            f"{'&'.join(f'scenario_id={scenario_id}' for scenario_id in selected_scenarios)}"
            f"&parameters_id={parameter_id}"
        )

        if self.embedded:
            response = HttpResponse(chart)
            response["HX-Redirect"] = url
        else:
            context = {"chart": chart, "table": df.to_html()}
            response = render(request, self.template_name, context)
            response["HX-Replace-Url"] = url
        return response


def save_filter_settings(request):
    name = request.POST.get("name")
    name_list = list(NamedFilterSettings.objects.values("name"))
    if name == "":
        return HttpResponse("Please enter a name.")
    if NamedFilterSettings.objects.filter(name=name).exists():
        return HttpResponse("Name already exists.")

    selected_scenarios = request.POST.getlist("scenario_id")
    filter_set = DataFilterSet(selected_scenarios, request.POST)
    if not filter_set.is_valid():
        return HttpResponse("Scenario or Other Form not valid.")

    selected_chart_type = request.POST.get("chart_type")
    selected_chart = graphs.CHART_DATA.get(selected_chart_type)
    form_class = selected_chart["form_class"]
    graph_filter_set = form_class(request.POST, data_filter_set=filter_set)
    if not graph_filter_set.is_valid():
        return HttpResponse("Graph or Display Form not valid.")

    else:
        # Create an instance of FilterSettings and assign the form data
        graph_filters = graph_filter_set.cleaned_data
        graph_filters["chart_type"] = selected_chart_type
        fs = FilterSettings(filter_set=filter_set.cleaned_data, graph_filter_set=graph_filters)
        fs.save()
        filter_settings = NamedFilterSettings(name=name, filter_settings=fs)
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
    if NamedFilterSettings.objects.filter(name=name).exists():
        return HttpResponse("This name already exits.", status=400)
    else:
        return HttpResponse("Your input is correct.", status=200)


def load_filter_settings(request):
    selected_scenarios = request.GET.getlist("scenario_id")
    name = request.GET.get("name")
    try:
        # need to check the name and if it is in the database
        filter_settings = NamedFilterSettings.objects.get(name=name).filter_settings

        filter_set = DataFilterSet(selected_scenarios, filter_settings.filter_set)

        selected_chart_type = filter_settings.graph_filter_set.pop("chart_type")
        selected_chart = graphs.CHART_DATA.get(selected_chart_type)
        form_class = selected_chart["form_class"]
        graph_filter_set = form_class(filter_settings.graph_filter_set, data_filter_set=filter_set)
        filter_setting_names = list(NamedFilterSettings.objects.values("name"))

        return render(
            request,
            "django_comparison_dashboard/dashboard.html",
            context=filter_set.get_context_data()
            | graph_filter_set.get_context_data()
            | {
                "name_list": filter_setting_names,
                "chart_type_form": ChartTypeForm({"chart_type": selected_chart_type}),
            },
        )
    except NamedFilterSettings.DoesNotExist:
        # needs a proper error
        return HttpResponse(status=404)


def change_chart_type(request):
    """
    called when type of chart is changed and refreshes the corresponding graph and display options.
    """
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
