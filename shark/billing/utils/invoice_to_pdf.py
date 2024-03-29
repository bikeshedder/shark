import tempfile

from dinbrief.document import Document
from dinbrief.invoice import ItemTable, TotalTable
from dinbrief.styles import styles
from dinbrief.template import BriefTemplate
from django.http import HttpResponse
from django.utils.formats import date_format
from django.utils.translation import override as trans_override
from PyPDF3 import PdfFileReader, PdfFileWriter
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.platypus.flowables import KeepTogether, Spacer

from ..models import Invoice, InvoiceTemplate


def as_http_response(
    invoice: Invoice, invoice_template: InvoiceTemplate
) -> HttpResponse:
    response = HttpResponse(content_type="application/pdf")
    return write_pdf(response, invoice, invoice_template)


def write_pdf(fh, invoice: Invoice, invoice_template: InvoiceTemplate):
    with trans_override(invoice.language):
        if invoice.type == Invoice.Type.INVOICE:
            terms = invoice_template.terms
            if callable(terms):
                terms = terms(invoice)
            else:
                if isinstance(terms, str):
                    terms = terms.split("\n")
                terms = [Paragraph(term, styles["Terms"]) for term in terms]
        else:
            terms = []

        template = BriefTemplate()

        #  |  Grappelli Drag and Drop auto positioning starts at 0
        #  |  Either implement own auto positioning or, simpler,
        # \|/ adjust the data for rendering
        for item in invoice.items:
            item.position += 1

        document = Document(
            sender=invoice.sender_lines,
            recipient=invoice.recipient_lines,
            date=date_format(invoice.created_at, "SHORT_DATE_FORMAT"),
            content=[
                Paragraph(
                    "%s %s"
                    % (
                        invoice.get_type_display(),
                        invoice.number,
                    ),
                    styles["Subject"],
                ),
                Spacer(template.CONTENT_WIDTH, 2 * mm),
                ItemTable(template, invoice),
                KeepTogether(TotalTable(template, invoice)),
                Spacer(template.CONTENT_WIDTH, 10 * mm),
            ]
            + terms,
        )

        if invoice_template.first_page_bg:
            with tempfile.TemporaryFile() as tmp:
                # Create content in a temporary file
                template.render(document, tmp)
                # Combine background with the content
                writer = PdfFileWriter()
                content = PdfFileReader(tmp)
                info_dict = writer._info.getObject()
                info_dict.update(content.getDocumentInfo())
                first_bg = PdfFileReader(invoice_template.first_page_bg.file, "rb")
                later_bg = PdfFileReader(
                    invoice_template.later_pages_bg.file
                    if invoice_template.later_pages_bg
                    else invoice_template.first_page_bg.file,
                    "rb",
                )
                bg = [first_bg.getPage(0), later_bg.getPage(0)]
                for i, page in enumerate(content.pages):
                    page.mergePage(bg[min(i, 1)])
                    page.compressContentStreams()
                    writer.addPage(page)
                writer.write(fh)
        else:
            # Render content directly to the HTTP response object if no
            # background images are configured.
            template.render(document, fh)

    return fh
