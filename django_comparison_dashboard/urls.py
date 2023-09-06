from django.urls import path

from django_comparison_dashboard import views
from .api import api

app_name = "django_comparison_dashboard"


urlpatterns = [
    path("api/", api.urls),
    path('index/', views.IndexView.as_view(), name='index'),
]
