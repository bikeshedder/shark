from datetime import date

from django_countries.fields import Country

from shark.utils.fields import get_address_fieldlist

from ..models import Invoice


class EmptyInvoiceTemplate(object):
    terms = "For presentational purposes only.\nA fake invoice"
    first_page_bg = None
    later_pages_bg = None


# Generate fake invoice models without customer relation
# To be able to preview templates and test pdf generation
class FakeInvoice(Invoice):
    customer = None
    number = "PREVIEW"
    template = EmptyInvoiceTemplate()

    @property
    def items(self):
        return []

    class Meta:
        managed = False
        proxy = True
        default_permissions = []


def create_fake_invoice():
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
        Country("DE"),
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
        Country("DE"),
    ]

    for field, value in [
        *zip(get_address_fieldlist("sender"), sender_values),
        *zip(get_address_fieldlist("recipient"), recipient_values),
    ]:
        setattr(invoice, field, value)

    invoice.language = "de"
    invoice.created_at = date.today()

    return invoice
