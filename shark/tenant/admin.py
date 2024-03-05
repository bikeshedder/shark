from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from shark.utils.fields import get_address_fieldlist

from .models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ["name"]}),
        (
            _("address"),
            {"fields": get_address_fieldlist("address")},
        ),
    )
