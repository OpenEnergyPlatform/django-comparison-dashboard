from django.http import HttpResponse
from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = "button.html"

def magic(request):
    return HttpResponse("Ta! Daaa!")