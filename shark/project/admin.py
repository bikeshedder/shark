from django.contrib import admin

from shark.tenant.admin import TenantAwareAdmin

from . import models


@TenantAwareAdmin
@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "customer", "active")
    list_editable = ("active",)
    list_filter = ("customer", "active")
    search_fields = ("name",)
    autocomplete_fields = ("customer",)
