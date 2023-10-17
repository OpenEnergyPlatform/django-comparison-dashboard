from django.http.response import HttpResponse
from django.views.generic import DetailView, FormView, ListView, TemplateView

from . import graphs, models, preprocessing, sources, utils


class IndexView(TemplateView):
    template_name = "django_comparison_dashboard/index.html"


class DashboardView(TemplateView):
    template_name = "django_comparison_dashboard/dashboard.html"


def scalar_data_plot(request):
    query = request.GET.dict()
    filters, groupby, units, plot_options = preprocessing.prepare_query(query)
    df = preprocessing.get_scalar_data(filters, groupby, units).to_dict(orient="records")
    return HttpResponse(graphs.bar_plot(df, plot_options).to_html())


def scalar_data_table(request):
    query = request.GET.dict()
    filters, groupby, units, plot_options = preprocessing.prepare_query(query)
    df = preprocessing.get_scalar_data(filters, groupby, units)
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

    def post(self, request):
        scenario_ids = request.POST.getlist("scenario_id")
        return utils.redirect_params("django_comparison_dashboard:dashboard", scenario_ids=scenario_ids)


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
