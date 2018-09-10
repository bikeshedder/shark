from django.urls import path

from . import views

app_name = 'issue'
urlpatterns = [
    path('create/', views.issue_create, name='issue_create'),
]
