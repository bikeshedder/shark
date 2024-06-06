from django.urls import path

from . import views

app_name = "project"
urlpatterns = [
    path("", views.index, name="index"),
    path("daily-report", views.daily_report, name="daily-report"),
]
