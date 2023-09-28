import json

from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView
from django.shortcuts import render

from django_comparison_dashboard.forms import Scenario


def index(request):
    filter_options = []
    if request.method == 'POST':
        form = Scenario(request.POST)
        if form.is_valid():
            filter_options = ["ID1", "ID2", "ID9"] # TODO get the options from data
            context = {'filter_options': filter_options}
            return render (request, 'django_comparison_dashboard/dashboard.html#filter-option', context)
        else:
            print(form.errors)  

    context = {'scenario_form': Scenario(), 'filter_options': filter_options}
    return render(request, 'django_comparison_dashboard/dashboard.html', context)
