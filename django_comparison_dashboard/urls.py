from django.urls import path

from . import views

app_name = "django_comparison_dashboard"

urlpatterns = [
    path("index/", views.index, name="index"),
    path("filters/", views.get_filters, name="filters"),
    path("scalars/", views.plot_scalar_data),
]
