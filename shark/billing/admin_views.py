from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.formats import date_format
from django.utils.translation import ugettext
from django.utils.translation import ungettext

from shark import get_model
from shark.billing.admin_forms import ImportItemsForm

InvoiceItem = get_model('billing.InvoiceItem')
Invoice = get_model('billing.Invoice')


permission_required('billing.add_invoice')
def invoice(request):
    items = InvoiceItem.objects.filter(invoice=None)
    return TemplateResponse(request, 'billing/admin/invoiceitem_invoice.html', {
        'items': items
    })


permission_required('billing.change_invoice')
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph
    from reportlab.platypus.flowables import Spacer

    from dinbrief.constants import CONTENT_WIDTH
    from dinbrief.document import Document
    from dinbrief.invoice import ItemTable, TotalTable
    from dinbrief.styles import styles
    from dinbrief.template import BriefTemplate

    response = HttpResponse(content_type='application/pdf')
    if 'download' in request.GET:
        filename = '%s.pdf' % invoice.number
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

    document = Document(
        sender=invoice.sender_lines,
        recipient=invoice.recipient_lines,
        date=date_format(invoice.created, 'SHORT_DATE_FORMAT'),
        content=[
            Paragraph('%s %s' % (ugettext(u'Invoice'), invoice.number), styles['Subject']),
            Spacer(CONTENT_WIDTH, 2*mm),
            ItemTable(invoice),
            TotalTable(invoice),
        ])
    template = BriefTemplate(response, document)
    template.build(document.content)

    return response


permission_required('billing.add_invoiceitem')
def import_items(request):
    if request.method == 'POST':
        form = ImportItemsForm(request.POST, request.FILES)
        if form.is_valid():
            items = form.cleaned_data['items']
            for item in items:
                item.save()
            messages.success(request, ungettext(
                '%(count)d invoice item imported.',
                '%(count)d invoice items imported.',
                len(items)
            ) % { 'count': len(items) })
    else:
        form = ImportItemsForm()
    from django.contrib.admin.helpers import AdminForm
    return TemplateResponse(request, 'billing/admin/import_items.html', {
        'form': form,
        'adminform': AdminForm(
            form=form,
            fieldsets=[
                (None, {
                    'fields': form.fields
                })
            ],
            prepopulated_fields={}),
        # The admin templates depend on those variables
        'add': True,
        'has_file_field': True,
        'errors': form.errors,
    })
