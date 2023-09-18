from django.http import HttpResponse
from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = "django_comparison_dashboard/dashboard.html"

def load_filter(request):
    return HttpResponse("Ta! Daaa!")