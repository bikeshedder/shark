import csv
from decimal import Decimal

from django.contrib import admin
from django.forms.widgets import HiddenInput
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext, ngettext
from django.utils.translation import gettext_lazy as _
from grappelli.forms import GrappelliSortableHiddenMixin

from shark import get_admin_change_url
from shark.customer.models import CustomerAddress
from shark.project.models import Project, Task
from shark.tenant.admin import tenant_aware_admin
from shark.utils.fields import get_address_fieldlist, get_language_from_country

from . import models


class ExcelSemicolon(csv.excel):
    delimiter = ";"


class InvoiceItemInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    model = models.InvoiceItem

    objects = []

    def get_extra(self, request, obj=None, **kwargs):
        """
        `extra` is the initial amount of rows to be displayed

        If an Invoice is created for a project with existing tasks
        `extra` should be equal to the number of tasks

        This also stores the tasks on the Inline instance
        so they can be used later to populate the fields

        Else return 0
        """
        if request.method == "GET":
            project_id = request.GET.get("project")
            if project_id:
                tasks = Task.objects.filter(
                    project__id=project_id, invoice_item__isnull=True
                ).all()
                self.objects = tasks
                return len(tasks)
        return 0


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            _("general"),
            {"fields": ("customer", "type", "language", "template")},
        ),
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
    list_editable = ["paid_at"]
    list_display_links = ["number"]
    list_select_related = True
    ordering = ("-created_at",)
    search_fields = ("number", "customer__number", "customer__name")
    list_filter = ("created_at", "paid_at", "type")
    date_hierarchy = "created_at"
    actions = ("total_value_action", "export_for_accounting")
    raw_id_fields = ["customer"]
    autocomplete_lookup_fields = {
        "fk": ["customer"],
    }

    def get_form(self, request, obj=None, **kwargs):
        """
        Prefill form fields as well as possible
        """
        form = super().get_form(request, obj, **kwargs)

        if obj is None and request.method == "GET":
            if request.tenant:
                tenant_address_dict = request.tenant.address.to_dict()
                for key, value in tenant_address_dict.items():
                    form.base_fields["sender_" + key].initial = value

            project_id = request.GET.get("project")
            if project_id:
                project = Project.objects.get(pk=project_id)

                form.base_fields["customer"].initial = project.customer
                customer_address = CustomerAddress.objects.get(
                    customer=project.customer
                )
                for key, value in customer_address.address.to_dict().items():
                    form.base_fields["recipient_" + key].initial = value
                form.base_fields["language"].initial = get_language_from_country(
                    customer_address.address.country
                )

                # Hide fields that are not supposed to be changed
                form.base_fields["customer"].widget = HiddenInput()
                form.base_fields["type"].widget = HiddenInput()

        return form

    def get_formset_kwargs(self, request, obj, inline, prefix):
        formset_params = super().get_formset_kwargs(request, obj, inline, prefix)

        if not obj.pk:
            # Fill item rows for billable tasks if Invoice is created for Project
            if request.method == "GET" and isinstance(inline, InvoiceItemInline):
                project_id = request.GET.get("project")
                if project_id:
                    tasks = inline.objects
                    formset_params |= {
                        "initial": [
                            {
                                "text": task.name,
                                "price": task.rate,
                                "begin": task.created_at_date,
                                "end": task.completed_at,
                                "unit": models.InvoiceItem.Units.HOURS,
                                "quantity": task.hours_expected,
                                "vat_rate": Decimal("0.19"),
                            }
                            for task in tasks
                        ]
                    }

        return formset_params

    @admin.display(description=_("Customer"), ordering="customer")
    def get_customer(self, obj):
        return format_html(
            '<a href="{}">{}</a>', get_admin_change_url(obj.customer), obj.customer
        )

    @admin.display(description=_("Recipient"))
    def get_recipient(self, obj):
        return format_html_join(
            "", "<p>{}</p>", ((line,) for line in obj.recipient_lines)
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
        return super().response_add(request, obj, *args, **kwargs)

    def response_change(self, request, obj, *args, **kwargs):
        obj.recalculate()
        obj.save()
        return super().response_change(request, obj, *args, **kwargs)

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
        writer = csv.writer(response, dialect=ExcelSemicolon)
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
            ),
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


@tenant_aware_admin
@admin.register(models.InvoiceTemplate)
class InvoiceTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "preview_invoice",
    )

    @admin.display(description="Preview")
    def preview_invoice(self, obj):
        url = reverse("billing_admin:invoice_template_preview_pdf", args=(obj.id,))
        return format_html('<a href="{}">Preview</a>', url)
