from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from shark.utils.time import time_to_decimal_hours

from .models import Project, Task


def index(request: HttpRequest, project_pk: int):
    project = get_object_or_404(
        Project.objects.prefetch_related("task_set").filter(pk=project_pk)
    )
    return render(request, "project/index.html", {"project": project})


@require_POST
def save_task(request: HttpRequest, project_pk: int, task_pk: int):
    time_str = request.POST.get("time_actual")
    time_dec = time_to_decimal_hours(time_str)
    Task.objects.filter(pk=task_pk).update(hours_actual=time_dec)
    return redirect("project:index", request.tenant.name.lower(), project_pk)
