from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from shark.tenant.admin import TenantAwareAdmin

from . import models


class CustomerAddressInline(admin.StackedInline):
    model = models.CustomerAddress
    extra = 0
    inline_classes = ["grp-collapse grp-open"]


class CustomerNoteInline(admin.StackedInline):
    model = models.CustomerNote
    extra = 0
    inline_classes = ["grp-collapse grp-open"]


@TenantAwareAdmin
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["number", "name", "address_html", "created_at"]
    date_hierarchy = "created_at"
    ordering = ["number", "name"]
    inlines = [CustomerAddressInline, CustomerNoteInline]

    search_fields = ["number", "name"]

    @admin.display(description=_("Billing address"))
    def address_html(self, instance: models.Customer):
        return instance.billing_address.lines_html
