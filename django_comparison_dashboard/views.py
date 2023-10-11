from django.http.response import HttpResponse
from django.shortcuts import render

from . import graphs, preprocessing, settings
from .forms import Filter, Scenario


def index(request):
    filter_form = Filter(options=[])
    context = {"scenario_form": Scenario(), "filter_form": filter_form}
    return render(request, "django_comparison_dashboard/dashboard.html", context)


def get_filters(request):
    form = Scenario(request.POST)
    if form.is_valid():
        tags_options = set()
        year_options = set()
        region_options = set()
        for scenario in form.cleaned_data["scenarios"]:
            tags_options.update(settings.DATASET[scenario]["Tags"])
            year_options.update(settings.DATASET[scenario]["Year"])
            region_options.update(settings.DATASET[scenario]["Region"])
        options = {
            "tags": [(item, item) for item in tags_options],
            "year": [(item, item) for item in year_options],
            "region": [(item, item) for item in region_options],
        }
        filter_form = Filter(options=options)
        return render(
            request,
            "django_comparison_dashboard/dashboard.html#filters",
            {"filter_form": filter_form},
        )
    else:
        print(form.errors)


def plot_scalar_data(request):
    query = request.GET.dict()
    filters, groupby, units, plot_options = preprocessing.prepare_query(query)
    df = preprocessing.get_scalar_data(filters, groupby, units).to_dict(orient="records")
    return HttpResponse(graphs.bar_plot(df, plot_options).to_html())
