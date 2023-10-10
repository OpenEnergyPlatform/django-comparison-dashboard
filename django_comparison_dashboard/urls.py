from django.urls import path

from . import views

app_name = "django_comparison_dashboard"


urlpatterns = [
    path("scalars/", views.plot_scalar_data),
]
