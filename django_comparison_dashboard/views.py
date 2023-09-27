import json
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "django_comparison_dashboard/dashboard.html"

def load_filter(request):
    scenario = request.GET.get('selected_item')
    #with open('../data/django_comparison_dashboard/dataset.json') as file:
    #    data = json.load(file)
    
    filter_options = ["ID1", "ID2", "ID9"]
    response = ""
    for filter in filter_options:
        print(filter)
        option = "<option value=\" " + filter + " \">" + filter + "</option>"
        response += option + " "

    return HttpResponse(response)