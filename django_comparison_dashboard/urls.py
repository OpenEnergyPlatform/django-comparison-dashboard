from django.urls import path

from .api import api

app_name = "django_comparison_dashboard"


urlpatterns = [
    path("api/", api.urls),
]
