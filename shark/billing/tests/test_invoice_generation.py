from django.http import HttpResponse
from django.test import TestCase

from ..utils import invoice_to_pdf
from ..utils.fake_invoice import create_fake_invoice


class TestInvoicePdfGeneration(TestCase):
    def test_pdf_generation_as_http_response(self):
        invoice = create_fake_invoice()
        response = invoice_to_pdf.as_http_response(invoice)
        self.assertIsInstance(response, HttpResponse)
        self.assertIs(response.status_code, 200)
