import tempfile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.formats import date_format
from django.utils.translation import ugettext
from django.utils.translation import ungettext
from django.utils.translation import override as trans_override
from pyPdf import PdfFileWriter, PdfFileReader

from shark import get_model
from shark.billing.admin_forms import ImportItemsForm

InvoiceItem = get_model('billing.InvoiceItem')
Invoice = get_model('billing.Invoice')

INVOICE_TERMS = settings.SHARK['INVOICE']['TERMS']


@permission_required('billing.add_invoice')
def invoice(request):
    items = InvoiceItem.objects.filter(invoice=None)
    return TemplateResponse(request, 'billing/admin/invoiceitem_invoice.html', {
        'items': items
    })


@permission_required('billing.change_invoice')
def invoice_pdf(request, number):
    invoice = get_object_or_404(Invoice, number=number)
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph
    from reportlab.platypus.flowables import Spacer

    from dinbrief.constants import CONTENT_WIDTH
    from dinbrief.document import Document
    from dinbrief.invoice import ItemTable, TotalTable
    from dinbrief.styles import styles
    from dinbrief.template import BriefTemplate

    with trans_override(invoice.language):

        response = HttpResponse(content_type='application/pdf')
        if 'download' in request.GET:
            filename = '%s.pdf' % invoice.number
            response['Content-Disposition'] = 'attachment; filename=%s' % filename

        if callable(INVOICE_TERMS):
            terms = INVOICE_TERMS(invoice)
        else:
            terms = [
                Paragraph(term, styles['Terms'])
                for term in INVOICE_TERMS
            ]

        document = Document(
            sender=invoice.sender_lines,
            recipient=invoice.recipient_lines,
            date=date_format(invoice.created, 'SHORT_DATE_FORMAT'),
            content=[
                Paragraph('%s %s' % (ugettext(u'Invoice'), invoice.number),
                        styles['Subject']),
                Spacer(CONTENT_WIDTH, 2*mm),
                ItemTable(invoice),
                TotalTable(invoice),
                Spacer(CONTENT_WIDTH, 10*mm),
            ] + terms)

        if settings.SHARK['INVOICE']['BACKGROUND']:
            with tempfile.TemporaryFile() as tmp:
                # Create content in a temporary file
                template = BriefTemplate(tmp, document)
                template.build(document.content)
                # Combine background with the content
                writer = PdfFileWriter()
                content = PdfFileReader(tmp)
                info_dict = writer._info.getObject()
                info_dict.update(content.getDocumentInfo())
                first_bg = PdfFileReader(file(
                        settings.SHARK['INVOICE']['BACKGROUND']['FIRST_PAGE']))
                later_bg = PdfFileReader(file(
                        settings.SHARK['INVOICE']['BACKGROUND']['LATER_PAGE']))
                bg = [first_bg.getPage(0), later_bg.getPage(0)]
                for i, page in enumerate(content.pages):
                    page.mergePage(bg[min(i, 1)])
                    page.compressContentStreams()
                    writer.addPage(page)
                writer.write(response)
        else:
            # Render content directly to the HTTP response object if no
            # background images are configured.
            template = BriefTemplate(response, document)
            template.build(document.content)

    return response


@permission_required('billing.add_invoiceitem')
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
