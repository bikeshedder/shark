from django.urls import path

from . import views

app_name = "project"
urlpatterns = [
    path("", views.index, name="index"),
    path("task/<int:task_pk>/save", views.save_task, name="save_task"),
]
