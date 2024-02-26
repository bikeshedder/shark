from django.contrib import admin
from django.utils.html import format_html_join
from django.utils.translation import gettext_lazy as _

from shark.customer import models


class CustomerAddressInline(admin.StackedInline):
    model = models.CustomerAddress
    extra = 0


class CustomerNoteInline(admin.StackedInline):
    model = models.CustomerNote
    extra = 0


class CustomerAdmin(admin.ModelAdmin):
    list_display = ["number", "name", "address_html", "created"]
    list_filter = ["created"]
    search_fields = ["number", "name"]
    date_hierarchy = "created"
    inlines = [CustomerAddressInline, CustomerNoteInline]
    ordering = ["name"]

    def address_html(self, instance):
        return format_html_join(
            "\n",
            "<p>{}</p>",
            ((address.lines_html,) for address in instance.address_set.all()),
        )

    address_html.short_description = _("Addresses")
    address_html.admin_order_field = "address"


if not models.Customer._meta.abstract:
    admin.site.register(models.Customer, CustomerAdmin)
