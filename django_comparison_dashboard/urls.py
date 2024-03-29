from django.urls import path

from . import forms, views

app_name = "django_comparison_dashboard"

urlpatterns = [
    path("index/", views.index, name="index"),
    path("filters/", views.get_filters, name="filters"),
    path("dashboard/", views.get_filters, name="dashboard"),
    path("scalars/", views.ScalarPlotView.as_view(), name="data_plot"),
    path("scalars/chart/", views.get_chart, name="data_chart"),
    path("scalars/data/", views.scalar_data_table, name="data_table"),
    path("scenarios/", views.ScenarioSelectionView.as_view(), name="scenarios"),
    path("scenario_detail/", views.ScenarioDetailView.as_view(), name="scenario_detail"),
    path("upload/", views.UploadView.as_view(), name="upload"),
    path("scenario_form/", views.ScenarioFormView.as_view(), name="scenario_form"),
    path("add_label/", views.KeyValueFormPartialView.as_view(prefix="labels", form=forms.LabelForm), name="add_label"),
    path(
        "remove_label/",
        views.KeyValueFormPartialView.as_view(prefix="labels", form=forms.LabelForm),
        name="remove_label",
    ),
    path("add_color/", views.KeyValueFormPartialView.as_view(prefix="colors", form=forms.ColorForm), name="add_color"),
    path(
        "remove_color/",
        views.KeyValueFormPartialView.as_view(prefix="colors", form=forms.ColorForm),
        name="remove_color",
    ),
    path("save/", views.save_filter_settings, name="save"),
    path("save/name", views.save_precheck_name, name="save_name"),
    path("load/", views.load_filter_settings, name="load"),
]
