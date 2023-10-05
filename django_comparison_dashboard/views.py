from django.shortcuts import render

from django_comparison_dashboard.forms import Scenario


def index(request):
    context = {"scenario_form": Scenario(), "filter_options": []}
    return render(request, "django_comparison_dashboard/dashboard.html", context)


def get_filters(request):
    form = Scenario(request.POST)
    if form.is_valid():
        filter_options = [
            "ID1",
            "ID2",
            "ID9",
        ]  # TODO get the options from data with form value
        context = {"filter_options": filter_options}
        return render(
            request, "django_comparison_dashboard/dashboard.html#filters", context
        )
    else:
        print(form.errors)
