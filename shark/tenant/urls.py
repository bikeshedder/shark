from django.urls import path

from . import views

app_name = "tenant"
urlpatterns = [
    path("", views.index, name="index"),
]
