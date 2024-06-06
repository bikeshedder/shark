from django.urls import path

from . import views

app_name = "tenant"
urlpatterns = [
    path("", views.index, name="index"),
    path("timesheet/", views.timesheet, name="timesheet"),
]
