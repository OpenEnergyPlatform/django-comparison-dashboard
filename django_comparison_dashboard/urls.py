from django.urls import path

from django_comparison_dashboard import views
from .api import api

app_name = "django_comparison_dashboard"


urlpatterns = [
    path('index/', views.IndexView.as_view(), name='index'),
]

hmtx_views = [
    path("magic/", views.magic, name='magic'),
]

urlpatterns += hmtx_views
