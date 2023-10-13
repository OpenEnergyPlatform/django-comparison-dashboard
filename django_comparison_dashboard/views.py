from django.http.response import HttpResponse
from django.views.generic import FormView, TemplateView

from . import graphs, models, preprocessing, sources


def plot_scalar_data(request):
    query = request.GET.dict()
    filters, groupby, units, plot_options = preprocessing.prepare_query(query)
    df = preprocessing.get_scalar_data(filters, groupby, units).to_dict(orient="records")
    return HttpResponse(graphs.bar_plot(df, plot_options).to_html())


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
