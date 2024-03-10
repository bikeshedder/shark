import csv
from decimal import Decimal

from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html, format_html_join, mark_safe
from django.utils.translation import gettext, ngettext
from django.utils.translation import gettext_lazy as _

from shark import get_admin_change_url, get_admin_changelist_url
from shark.tenant.admin import TenantAwareAdmin
from shark.utils.fields import get_address_fieldlist

from . import models


class excel_semicolon(csv.excel):
    delimiter = ";"


class InvoiceItemInline(admin.TabularInline):
    model = models.InvoiceItem
    extra = 3
    ordering = ("position",)
    exclude = ("customer",)


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    fieldsets = (
        (_("general"), {"fields": ("customer", "type", "language")}),
        (
            _("sender"),
            {"fields": get_address_fieldlist("sender")},
        ),
        (
            _("recipient"),
            {"fields": get_address_fieldlist("recipient")},
        ),
    )
    inlines = [InvoiceItemInline]
    list_display = (
        "number",
        "get_customer",
        "get_recipient",
        "net",
        "gross",
        "created_at",
        "paid_at",
        "is_okay",
        "invoice_pdf",
        "correction_pdf",
    )
    list_editable = ("paid_at",)
    list_display_links = ("number",)
    list_select_related = True
    ordering = ("-created_at",)
    search_fields = ("number", "customer__number", "customer__name")
    list_filter = ("created_at", "paid_at", "type")
    date_hierarchy = "created_at"
    actions = ("total_value_action", "export_for_accounting")
    raw_id_fields = ("customer",)
    autocomplete_lookup_fields = {
        "fk": ["customer"],
    }

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if obj is None:
            tenant_address_dict = request.tenant.address.as_dict
            for key, value in tenant_address_dict.items():
                form.base_fields["sender_" + key].initial = value

        return form

    @admin.display(description=_("Customer"), ordering="customer")
    def get_customer(self, obj):
        return format_html(
            '<a href="{}">{}</a>', get_admin_change_url(obj.customer), obj.customer
        )

    @admin.display(description=_("Recipient"))
    def get_recipient(self, obj):
        return format_html_join(
            mark_safe("<br>"), "{}", ((line,) for line in obj.recipient_lines)
        )

    @admin.display(description="Invoice")
    def invoice_pdf(self, obj):
        view_url = reverse("billing_admin:invoice_pdf", args=(obj.number,))
        download_url = reverse("billing_admin:invoice_pdf", args=(obj.number,))
        return format_html(
            '<a href="{}">View</a> | <a href="{}?download">Download</a>',
            view_url,
            download_url,
        )

    @admin.display(description="Correction")
    def correction_pdf(self, obj):
        view_url = reverse("billing_admin:correction_pdf", args=(obj.number,))
        download_url = reverse("billing_admin:correction_pdf", args=(obj.number,))
        return format_html(
            '<a href="{}">View</a> | <a href="{}?download">Download</a>',
            view_url,
            download_url,
        )

    def response_add(self, request, obj, *args, **kwargs):
        obj.recalculate()
        obj.save()
        return super(InvoiceAdmin, self).response_add(request, obj, *args, **kwargs)

    def response_change(self, request, obj, *args, **kwargs):
        obj.recalculate()
        obj.save()
        return super(InvoiceAdmin, self).response_change(request, obj, *args, **kwargs)

    @admin.display(description=_("Calculate total value of selected invoices"))
    def total_value_action(self, request, queryset):
        net = Decimal(0)
        gross = Decimal(0)
        for invoice in queryset:
            net += invoice.net
            gross += invoice.gross
        value = gettext("%(net)s net, %(gross)s gross") % {"net": net, "gross": gross}
        self.message_user(
            request,
            ngettext(
                "Total value of %(count)d invoice: %(value)s",
                "Total value of %(count)d invoices: %(value)s",
                len(queryset),
            )
            % {"count": len(queryset), "value": value},
        )

    @admin.display(description="Export selected invoices for accounting")
    def export_for_accounting(self, request, queryset):
        queryset = queryset.select_related("customer")
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=invoices.csv"
        writer = csv.writer(response, dialect=excel_semicolon)
        cols = [
            ("created_at", lambda iv: iv.created_at.date()),
            ("paid_at", None),
            ("number", None),
            ("net", None),
            ("gross", None),
            ("vat_rate", lambda iv: iv.vat_items[0][0] if iv.vat_items else 0),
            ("vat", lambda iv: iv.vat_items[0][1] if iv.vat_items else 0),
            ("payment_type", None),
            ("customer_number", lambda iv: iv.customer.number),
            ("customer_vatin", lambda iv: iv.customer.vatin),
            (
                "address",
                lambda iv: iv.recipient,
            ),  # FIXME replace by new customer.billing_address
        ]
        writer.writerow([c[0] for c in cols])
        for invoice in queryset:
            writer.writerow(
                [
                    accessor(invoice) if accessor else getattr(invoice, name)
                    for name, accessor in cols
                ]
            )
        return response


@admin.register(models.InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "invoice",
        "position",
        "sku",
        "text",
        "begin",
        "end",
        "quantity",
        "price",
        "total",
        "discount",
        "vat_rate",
    )
    list_display_links = ("position", "text")
    list_filter = ("begin", "end", "vat_rate")
    ordering = ("customer__number", "invoice__number", "position")
    search_fields = ("invoice__number", "customer__number", "sku", "text")
    actions = ("action_create_invoice",)
    autocomplete_fields = ("customer", "invoice")
    raw_id_fields = ("invoice",)

    @admin.display(description=_("Create invoice(s) for selected item(s)"))
    def action_create_invoice(self, request, queryset):
        # customer_id -> items
        items_dict = {}
        # [(customer, items)]
        customer_items_list = []
        for item in queryset.filter(invoice=None).order_by("text"):
            try:
                items = items_dict[item.customer_id]
            except KeyError:
                items = items_dict[item.customer_id] = []
                customer_items_list.append((item.customer, items))
            items.append(item)
        # create invoices
        for customer, items in customer_items_list:
            invoice = models.Invoice()
            invoice.customer = customer
            invoice.save()
            for position, item in enumerate(items, 1):
                item.position = position
                item.invoice = invoice
                item.save()
            invoice.recalculate()
            invoice.save()
        return HttpResponseRedirect(get_admin_changelist_url(models.Invoice))


@TenantAwareAdmin
@admin.register(models.InvoiceTemplate)
class InvoiceTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_selected",
        "preview_invoice",
    )

    list_editable = ("is_selected",)

    @admin.display(description="Preview")
    def preview_invoice(self, obj):
        url = reverse("billing_admin:invoice_template_preview_pdf", args=(obj.id,))
        return format_html('<a href="{}">Preview</a>', url)
