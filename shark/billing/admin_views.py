from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.formats import date_format
from django.contrib.auth.decorators import permission_required

from shark import get_model
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
            Paragraph('%s %s' % (_('Invoice'), invoice.number), styles['Subject']),
            Spacer(CONTENT_WIDTH, 2*mm),
            ItemTable(invoice),
            TotalTable(invoice),
        ])
    template = BriefTemplate(response, document)
    template.build(document.content)

    return response
