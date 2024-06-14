from io import BytesIO

from django.http import HttpResponse
from django.test import TestCase
from django_countries.fields import Country
from PyPDF3 import PdfFileReader

from ..utils import invoice_to_pdf
from ..utils.fake_invoice import create_fake_invoice


class TestInvoicePdfGeneration(TestCase):
    def test_pdf_generation_as_http_response(self):
        invoice = create_fake_invoice()
        response = invoice_to_pdf.as_http_response(invoice)
        self.assertIsInstance(response, HttpResponse)
        self.assertIs(response.status_code, 200)

    def test_address_countries(self):
        invoice = create_fake_invoice()
        invoice.sender.country = Country("DE")
        invoice.recipient.country = Country("DE")

        # Omitted if same country
        response = invoice_to_pdf.as_http_response(invoice)
        content = PdfFileReader(BytesIO(response.content)).pages[0].extractText()
        self.assertFalse("Germany" in content)

        # Present if different countries
        invoice.sender.country = Country("KH")
        response = invoice_to_pdf.as_http_response(invoice)
        content = PdfFileReader(BytesIO(response.content)).pages[0].extractText()
        self.assertTrue("Germany" in content)
        self.assertTrue("Cambodia" in content)
