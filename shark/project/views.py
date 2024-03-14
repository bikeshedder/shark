from django.http import HttpRequest
from django.shortcuts import render

from shark.project.models import Task


def index(request: HttpRequest, project_pk: int):
    tasks = Task.objects.filter(project__pk=project_pk, project__tenant=request.tenant)
    return render(request, "project/index.html", {"tasks": tasks})
