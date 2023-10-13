from django.urls import path

from . import views

app_name = "django_comparison_dashboard"


urlpatterns = [
    path("scalars/", views.scalar_data_plot),
    path("scalars/data/", views.scalar_data_table),
    path("upload/", views.UploadView.as_view(), name="upload"),
    path("scenario_form/", views.ScenarioFormView.as_view(), name="scenario_form"),
]
