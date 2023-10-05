from django.shortcuts import render

from . import settings
from .forms import Scenario


def index(request):
    context = {"scenario_form": Scenario(), "filter_options": []}
    return render(request, "django_comparison_dashboard/dashboard.html", context)


def get_filters(request):
    form = Scenario(request.POST)
    if form.is_valid():
        filter_options = set()
        for scenario in form.cleaned_data["scenarios"]:
            filter_options.update(settings.DATASET[scenario]["Tags"])
        return render(
            request,
            "django_comparison_dashboard/dashboard.html#filters",
            {"filter_options": filter_options},
        )
    else:
        print(form.errors)
