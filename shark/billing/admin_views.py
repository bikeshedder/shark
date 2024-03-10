from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.translation import ngettext

from .admin_forms import ImportItemsForm
from .models import Invoice, InvoiceItem, InvoiceTemplate
from .utils import invoice_to_pdf
from .utils.fake_invoice import create_fake_invoice


@permission_required("billing.add_invoice")
def invoice(request):
    items = InvoiceItem.objects.filter(invoice=None)
    return TemplateResponse(
        request, "billing/admin/invoiceitem_invoice.html", {"items": items}
    )


@permission_required("billing.add_invoicetemplate")
def preview_invoice_template(request, id):
    invoice_template = get_object_or_404(InvoiceTemplate, id=id)
    invoice = create_fake_invoice()
    return invoice_to_pdf.as_http_response(invoice, invoice_template)


@permission_required("billing.change_invoice")
def invoice_pdf(request, number, correction=False):
    invoice = get_object_or_404(Invoice, number=number)
    if correction:
        invoice = invoice.correction

    invoice_template = request.tenant.selected_invoice_template
    response = invoice_to_pdf.as_http_response(invoice, invoice_template)
    if "download" in request.GET:
        filename = "%s.pdf" % invoice.number
        response["Content-Disposition"] = "attachment; filename=%s" % filename

    return response


@permission_required("billing.change_invoice")
def correction_pdf(request, number):
    return invoice_pdf(request, number, correction=True)


@permission_required("billing.add_invoiceitem")
def import_items(request):
    if request.method == "POST":
        form = ImportItemsForm(request.POST, request.FILES)
        if form.is_valid():
            items = form.cleaned_data["items"]
            for item in items:
                item.save()
            messages.success(
                request,
                ngettext(
                    "%(count)d invoice item imported.",
                    "%(count)d invoice items imported.",
                    len(items),
                )
                % {"count": len(items)},
            )
    else:
        form = ImportItemsForm()
    from django.contrib.admin.helpers import AdminForm

    return TemplateResponse(
        request,
        "billing/admin/import_items.html",
        {
            "form": form,
            "adminform": AdminForm(
                form=form,
                fieldsets=[(None, {"fields": form.fields})],
                prepopulated_fields={},
            ),
            # The admin templates depend on those variables
            "add": True,
            "has_file_field": True,
            "errors": form.errors,
        },
    )
