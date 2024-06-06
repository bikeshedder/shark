from datetime import datetime

from django import forms
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods
from django_htmx.http import HttpResponseClientRefresh

from shark.project.forms import DailyReportDateForm, DailyReportEntryForm

from .models import Project, Task, TaskTimeEntry


def index(request: HttpRequest, project_pk: int):
    project = get_object_or_404(
        Project.objects.prefetch_related("task_set").filter(
            tenant=request.tenant, pk=project_pk
        )
    )
    tasks = project.task_set.all()

    daily_report_context = daily_report(request, project=project)

    return render(
        request,
        "project/index.html",
        {
            "project": project,
            "tasks": tasks,
            "report_form": daily_report_context,
            "report_date_form": DailyReportDateForm(
                {"date": daily_report_context["date"]}
            ),
        },
    )


@require_http_methods(["GET", "POST"])
def daily_report(request: HttpRequest, project_pk=None, project=None):
    if project is None:
        project = get_object_or_404(
            Project.objects.prefetch_related("task_set").filter(
                tenant=request.tenant, pk=project_pk
            )
        )
    tasks = project.task_set.all()

    formset = forms.inlineformset_factory(
        Task, TaskTimeEntry, form=DailyReportEntryForm, extra=1
    )

    if request.method == "POST":
        date_param = request.POST.get("date")
        date = datetime.strptime(date_param, "%Y-%m-%d").date()
        task_formsets = [
            {
                "name": task.name,
                "formset": formset(request.POST, instance=task, prefix=task.id),
            }
            for task in tasks
        ]
        if all([entry["formset"].is_valid() for entry in task_formsets]):
            for entry in task_formsets:
                for form in entry["formset"]:
                    obj = form.save(commit=False)
                    obj.date = date
                    obj.employee = request.tenant_member
                    obj.save()

            return HttpResponseClientRefresh()

    if request.method == "GET":
        date_param = request.GET.get("date", None)
        date = (
            datetime.strptime(date_param, "%Y-%m-%d").date()
            if date_param
            else now().date()
        )
        task_formsets = [
            {
                "name": task.name,
                "formset": formset(
                    instance=task,
                    prefix=task.id,
                    queryset=TaskTimeEntry.objects.filter(
                        date=date, employee=request.tenant_member
                    ),
                ),
            }
            for task in tasks
        ]

    context = {
        "project_id": project.id,
        "date": date.isoformat(),
        "tasks": task_formsets,
    }

    if not request.htmx:
        return context
    else:
        return render(
            request, "project/partials/daily-report-form.html", {"data": context}
        )
