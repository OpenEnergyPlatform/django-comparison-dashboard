from django.urls import path

from . import views

app_name = "django_comparison_dashboard"


urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("scalars/", views.scalar_data_plot),
    path("scalars/data/", views.scalar_data_table),
    path("scenarios/", views.ScenarioSelectionView.as_view(), name="scenarios"),
    path("scenario_detail/", views.ScenarioDetailView.as_view(), name="scenario_detail"),
    path("upload/", views.UploadView.as_view(), name="upload"),
    path("scenario_form/", views.ScenarioFormView.as_view(), name="scenario_form"),
]
