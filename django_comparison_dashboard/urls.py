from django.urls import path

from . import views

app_name = "django_comparison_dashboard"

urlpatterns = [
    path("index/", views.index, name="index"),
    path("filters/", views.get_filters, name="filters"),
    path("dashboard/", views.get_filters, name="dashboard"),
    path("scalars/", views.scalar_data_plot, name="data_plot"),
    path("scalars/data/", views.scalar_data_table, name="data_table"),
    path("scenarios/", views.ScenarioSelectionView.as_view(), name="scenarios"),
    path("scenario_detail/", views.ScenarioDetailView.as_view(), name="scenario_detail"),
    path("upload/", views.UploadView.as_view(), name="upload"),
    path("scenario_form/", views.ScenarioFormView.as_view(), name="scenario_form"),
    path("add_label/", views.add_label_form, name="add_label_form"),
    path("add_color/", views.add_color_form, name="add_color_form"),
    path("save/", views.save_filter_settings, name="save"),
    path("save/name", views.save_precheck_name, name="save_name"),
    path("load/", views.load_filter_settings, name="load"),
]
