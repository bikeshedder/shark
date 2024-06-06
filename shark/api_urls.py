from django.urls import include, path

app_name = "api"
urlpatterns = [
    path("project/", include("shark.project.api.urls")),
]
