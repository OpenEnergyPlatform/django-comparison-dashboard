import json
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView
from django.shortcuts import render


class IndexView(TemplateView):
    template_name = "django_comparison_dashboard/dashboard.html"

def load_filter(request):
    scenario = request.GET.get('scenario')
    
    #with open('data/django_comparison_dashboard/dataset.json') as file:
    #    data = json.load(file)

    #filter_options = data[scenario]["Tags"]
    #response = ""
    #for filter in filter_options:
    #    print(filter)
    #    option = "<option value=\" " + filter + " \">" + filter + "</option>"
    #    response += option + " "

    filtered_values = ["ID1", "ID2", "ID9"]
    return render(request, {'filtered_values': filtered_values})