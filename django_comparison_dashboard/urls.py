from django.contrib import admin
from django.urls import path

from .api import api

app_name = "django_comparison_dashboard"


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
