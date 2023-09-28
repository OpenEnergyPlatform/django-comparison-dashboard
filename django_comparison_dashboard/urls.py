from django.urls import path

from django_comparison_dashboard import views

app_name = "django_comparison_dashboard"


urlpatterns = [
    path('index/', views.index, name='index'),
]
