from django.urls import path

from django_comparison_dashboard import views

app_name = "django_comparison_dashboard"


urlpatterns = [
    path('index/', views.IndexView.as_view(), name='index'),
]

hmtx_views = [
    path("load-filter/", views.load_filter, name='filter'),
]

urlpatterns += hmtx_views
