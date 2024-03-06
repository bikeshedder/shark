from datetime import date

from shark.utils.fields import get_address_fieldlist

from ..models import Invoice, InvoiceTemplate


# Generate fake invoice models without customer relation
# To be able to preview templates and test pdf generation
class FakeInvoice(Invoice):
    customer = None
    number = "PREVIEW"

    @property
    def items(self):
        return []

    class Meta:
        managed = False
        proxy = True


class FakeInvoiceTemplate(InvoiceTemplate):
    terms = []
    first_page_bg = None
    later_pages_bg = None

    class Meta:
        managed = False
        proxy = True


def create_fake_invoice(template=None):
    invoice = FakeInvoice()

    sender_values = [
        "Awesome Company",
        "",
        "",
        "Invoice Valley",
        "69",
        "PDFTown",
        "42069",
        "",
    ]

    recipient_values = [
        "Invoice recipient",
        "",
        "",
        "Recipient street",
        "10",
        "Chadville",
        "1337",
        "",
    ]

    for field, value in [
        *zip(get_address_fieldlist("sender"), sender_values),
        *zip(get_address_fieldlist("recipient"), recipient_values),
    ]:
        setattr(invoice, field, value)

    invoice.language = "de"
    invoice.created_at = date.today()

    if template is None:
        template = FakeInvoiceTemplate()
        template.terms = ["Terms and conditions", "Lorem ipsum dolor...", "Etc"]

    invoice.template = template

    return invoice
