from django.contrib import admin
from django.utils.html import format_html_join
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
    list_filter = ["created_at"]
    search_fields = ["number", "name"]
    date_hierarchy = "created_at"
    inlines = [CustomerAddressInline, CustomerNoteInline]
    ordering = ["number", "name"]

    def address_html(self, instance):
        return format_html_join(
            "\n",
            "<p>{}</p>",
            ((address.lines_html,) for address in instance.address_set.all()),
        )

    address_html.short_description = _("Addresses")
    address_html.admin_order_field = "address"
