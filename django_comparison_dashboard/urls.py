from django.urls import path

from . import forms, views

app_name = "django_comparison_dashboard"

urlpatterns = [
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("scalars/", views.ScalarView.as_view(), name="render_data"),
    path("scalars/chart/", views.ScalarView.as_view(embedded=True), name="data_chart"),
    path("scenarios/", views.ScenarioSelectionView.as_view(), name="scenarios"),
    path("scenario_detail/", views.ScenarioDetailView.as_view(), name="scenario_detail"),
    path("upload/", views.UploadView.as_view(), name="upload"),
    path("scenario_form/", views.ScenarioFormView.as_view(), name="scenario_form"),
    path("add_label/", views.KeyValueFormPartialView.as_view(prefix="labels", form=forms.LabelForm), name="add_label"),
    path("remove_label/",views.KeyValueFormPartialView.as_view(prefix="labels", form=forms.LabelForm),
        name="remove_label"),
    path("add_color/", views.KeyValueFormPartialView.as_view(prefix="colors", form=forms.ColorForm), name="add_color"),
    path("remove_color/",views.KeyValueFormPartialView.as_view(prefix="colors", form=forms.ColorForm),
         name="remove_color"),
    path("save/", views.save_filter_settings, name="save"),
    path("save/name", views.save_precheck_name, name="save_name"),
    path("load/", views.load_filter_settings, name="load"),
    path("change_chart_type/", views.change_chart_type, name="change_chart_type"),
]
