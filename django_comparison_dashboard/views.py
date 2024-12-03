from io import StringIO

from django.forms.formsets import formset_factory
from django.http.response import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import DetailView, FormView, ListView, TemplateView, View
from django_energysystem_viewer.views import get_excel_data
from django_htmx.http import retarget

from . import graphs, models, preprocessing, sources
from .forms import ChartTypeForm, DataFilterSet  # noqa: F401
from .helpers import save_filters
from .models import NamedFilterSettings


class FormProcessingError(Exception):
    def __init__(self, response, message="Form processing failed"):
        self.response = response
        super().__init__(message)


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


def get_chart_and_table_from_request(request, as_html=True) -> tuple:
    """Render chart and data table from request."""
    selected_scenarios = request.GET.getlist("scenario_id")

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

    filter_set = DataFilterSet(selected_scenarios, selected_chart_type, filter_parameters)
    if not filter_set.is_valid():
        response = render(
            request,
            "django_comparison_dashboard/dashboard.html#filters",
            context=filter_set.get_context_data(),
        )
        response = retarget(response, "#filters")
        raise FormProcessingError(response, message="Filter set not valid.")
    df = preprocessing.get_scalar_data(filter_set)

    selected_chart = graphs.CHART_DATA.get(selected_chart_type)
    form_class = selected_chart["form_class"]
    graph_filter_set = form_class(graph_parameters, data_filter_set=filter_set)
    if not graph_filter_set.is_valid():
        response = render(
            request,
            "django_comparison_dashboard/dashboard.html#graph_options",
            context=graph_filter_set.get_context_data(),
        )
        response = retarget(response, "#graph_options")
        raise FormProcessingError(response, message="Graph filter set not valid.")
    chart_function = selected_chart["chart_function"]
    chart = chart_function(df, graph_filter_set)
    if as_html:
        table = df.to_html()
        chart = chart.to_html(config={"toImageButtonOptions": {"format": "svg"}})
    else:
        table = df
    return chart, table


class DashboardView(TemplateView):
    """
    Initializes dashboard

    Including filters and chart/table if parameters are given.
    Example for incoming request: localhost:8000/dashboard/?scenario_id=5&scenario_id=10
    """

    template_name = "django_comparison_dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        abbreviations = get_excel_data("SEDOS-structure-all", "abbreviations")
        abbreviation_list = abbreviations["abbreviations"].unique()
        selected_scenarios = self.request.GET.getlist("scenario_id")
        filter_setting_names = list(NamedFilterSettings.objects.values("name"))
        chart_type = self.request.GET.get("chart_type", "bar")
        filter_set = DataFilterSet(selected_scenarios, chart_type)
        graph_filter_set = graphs.CHART_DATA["bar"]["form_class"]()
        chart_type_form = ChartTypeForm()
        return (
            filter_set.get_context_data()
            | graph_filter_set.get_context_data()
            | {
                "name_list": filter_setting_names,
                "chart_type_form": chart_type_form,
                "abbreviation_list": abbreviation_list,
                "structure_name": "SEDOS-structure-all",
            }
        )


class ScalarView(TemplateView):
    template_name = "django_comparison_dashboard/partials/plot.html"
    embedded = False

    def get(self, request, *args, **kwargs):
        try:
            chart, table = get_chart_and_table_from_request(request)
        except:  # noqa: E722
            return render(
                request,
                "django_comparison_dashboard/partials/error.html",
                context={"requested_url": request.get_full_path()},
            )

        if request.GET.get("download") == "true":
            chart, table = get_chart_and_table_from_request(request, as_html=False)
            csv_buffer = StringIO()
            table.to_csv(csv_buffer, index=False)
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="data.csv"'
            response.write(csv_buffer.getvalue())
            csv_buffer.close()
            return response

        if "parameters_id" not in request.GET:
            parameter_id = save_filters(request.GET)
        else:
            parameter_id = request.GET["parameters_id"]

        selected_scenarios = request.GET.getlist("scenario_id")
        url = (
            f"{request.path}?"
            f"{'&'.join(f'scenario_id={scenario_id}' for scenario_id in selected_scenarios)}"
            f"&parameters_id={parameter_id}"
        )

        if self.embedded:
            response = HttpResponse(chart)
            response["HX-Redirect"] = url
        else:
            context = {"chart": chart, "table": table}
            response = render(request, self.template_name, context)
        return response


def save_filter_settings(request):
    name = request.POST.get("name")
    if name == "":
        return HttpResponse("Please enter a name.")
    if NamedFilterSettings.objects.filter(name=name).exists():
        return HttpResponse("Name already exists.")

    save_filters(request.POST, name=name)

    response = render(
        request,
        "django_comparison_dashboard/dashboard.html#load_settings",
        {"name_list": list(NamedFilterSettings.objects.values("name"))},
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
        selected_chart_type = filter_settings.graph_filter_set.pop("chart_type")
        filter_set = DataFilterSet(selected_scenarios, selected_chart_type, filter_settings.filter_set)
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
        form = self.get_source().form
        try:
            scenario_list = self.get_source().list_scenarios()
        except NotImplementedError:
            scenario_list = []
        if scenario_list:
            form.base_fields["scenario_id"].choices = [(scenario.id, scenario.id) for scenario in scenario_list]
        return form

    def form_valid(self, form):
        source = self.get_source()
        scenario = source.scenario(**form.cleaned_data)
        if models.Result.objects.filter(source__name=source.name, name=scenario.id).exists():
            return HttpResponse("Scenario already present in database.")
        scenario.download()
        return HttpResponse(f"Uploaded scenario '{scenario}'.")
