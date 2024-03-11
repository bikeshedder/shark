from django.contrib import admin

from shark.tenant.admin import TenantAwareAdmin

from . import models


@TenantAwareAdmin
@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "customer", "active"]
    list_editable = ["active"]
    list_filter = ["customer", "active"]
    search_fields = ["name"]


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "project",
        "created_at_date",
        "time_expected",
        "time_actual",
        "due_by",
        "finished_at",
    )

    list_filter = ["project", "created_at", "due_by", "finished_at"]
