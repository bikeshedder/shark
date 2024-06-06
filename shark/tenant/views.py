import calendar
import datetime
import decimal

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.formats import date_format

from shark.project.models import Project, TaskTimeEntry

from .models import TenantMember
from .typst.timesheet import TaskDict, TaskInfo, generate_timesheet


def index(request: HttpRequest):
    if request.tenant_member.role == TenantMember.Role.ADMIN:
        projects = Project.objects.filter(tenant=request.tenant)
    else:
        projects = request.tenant_member.projects
    return render(request, "tenant/index.html", {"projects": projects})


# TODO: i18n month and day names
def timesheet(request: HttpRequest):
    project_pk = request.GET.get("project", "")
    project = get_object_or_404(
        Project.objects.filter(pk=project_pk, tenant=request.tenant)
    )

    today = datetime.date.today()
    year, month = (
        (int(request.GET["year"]) if "year" in request.GET else today.year),
        (int(request.GET["month"]) if "month" in request.GET else today.month),
    )

    queryset = (
        TaskTimeEntry.objects.filter(
            date__month=month,
            date__year=year,
            task__project=project,
            employee=request.tenant_member,
        )
        .select_related("task")
        .order_by("date")
    )

    entries = queryset.all()
    num_entries, entry_idx = len(entries), 0
    current_entry = entries[0] if num_entries > 0 else None

    if request.method == "GET":
        """
        Collect time entries for each day of the selected month
        Using index iteration to not have to filter over the same queryset repeatedly
        """

        calendar_context = {
            "data": [],
            "year": year,
            "month": month,
            "project_id": project_pk,
        }

        for week in calendar.Calendar().monthdayscalendar(year, month):
            week_entries = []
            for day_in_month in week:
                day_entries = []
                while current_entry and current_entry.date.day == day_in_month:
                    day_entries.append(current_entry)
                    entry_idx += 1
                    current_entry = (
                        entries[entry_idx] if entry_idx < num_entries else None
                    )

                week_entries.append(
                    {
                        "day": day_in_month,
                        "entries": day_entries,
                        "hours": sum(entry.duration for entry in day_entries),
                    }
                )

            calendar_context["data"].append(week_entries)

        # Render only calendar fields
        if request.htmx:
            return render(
                request, "tenant/partials/calendar_fields.html", calendar_context
            )

        months = [str(i) for i in range(1, 13)]
        years = list(range(2024, today.year + 1))

        # Render whole page
        return render(
            request,
            "tenant/timesheet.html",
            {
                **calendar_context,
                "months": months,
                "years": years,
            },
        )

    # Respond with pdf timesheet
    if request.method == "POST":
        timesheet_data = {
            "employee_name": str(request.tenant_member),
            "project_name": project.name,
            "year": year,
            "month": month,
            "days": [],
            "hours_total": decimal.Decimal("0"),
        }

        day_names = {
            0: "Mo",
            1: "Di",
            2: "Mi",
            3: "Do",
            4: "Fr",
            5: "Sa",
            6: "So",
        }

        for day_in_month, day_number in calendar.Calendar().itermonthdays2(year, month):
            # Skip days outside of selected month
            if day_in_month == 0:
                continue

            day_data = {
                "date": date_format(datetime.date(year, month, day_in_month)),
                "day_name": day_names[day_number],
                "tasks": [],
            }

            def find_task_entry_by_name(entries: list, value: str):
                return next((x for x in entries if x["name"] == value), None)

            while current_entry and current_entry.date.day == day_in_month:
                # Get or create clocked task
                task = find_task_entry_by_name(
                    day_data["tasks"], current_entry.task.name
                )

                if not task:
                    task: TaskDict = {
                        "name": current_entry.task.name,
                        "hours": current_entry.duration,
                        "subtasks": [],
                    }
                    day_data["tasks"].append(task)
                else:
                    task["hours"] += current_entry.duration

                timesheet_data["hours_total"] += current_entry.duration

                # If time_entry has description add it as a subtask
                if current_entry.description:
                    subtask = find_task_entry_by_name(
                        task["subtasks"], current_entry.description
                    )

                    if not subtask:
                        subtask: TaskInfo = {
                            "name": current_entry.description,
                            "hours": current_entry.duration,
                        }
                        task["subtasks"].append(subtask)
                    else:
                        subtask["hours"] += current_entry.duration

                entry_idx += 1
                current_entry = entries[entry_idx] if entry_idx < num_entries else None

            timesheet_data["days"].append(day_data)

        return HttpResponse(
            generate_timesheet(timesheet_data),
            content_type="application/pdf",
        )
