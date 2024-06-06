from datetime import date

from django.db import IntegrityError
from django.test import TestCase

from shark.billing.models import Invoice
from shark.customer.models import Customer
from shark.tenant.models import Tenant

from ..utils import InvoiceNumberGenerators

CURRENT_YEAR = date.today().year


class TestYearCustomerNGenerator(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create(
            name="test-tenant",
            invoice_number_generator=InvoiceNumberGenerators.YEAR_CUSTOMER_N,
        )
        cls.customer = Customer.objects.create(tenant=cls.tenant, name="Anna")

    def test_first_and_next(self):
        invoice = Invoice.objects.create(customer=self.customer)
        self.assertEqual(invoice.number, f"{CURRENT_YEAR}-{self.customer.number}-01")

        invoice2 = Invoice.objects.create(customer=self.customer)
        self.assertEqual(invoice2.number, f"{CURRENT_YEAR}-{self.customer.number}-02")

    def test_different_customer(self):
        customer = Customer.objects.create(tenant=self.tenant, name="Bernd")
        invoice = Invoice.objects.create(customer=customer)
        self.assertEqual(invoice.number, f"{CURRENT_YEAR}-{customer.number}-01")

    def test_uniqueness(self):
        with self.assertRaises(IntegrityError):
            Invoice.objects.create(number=f"{self.customer.number}-01")


# def test_prefix(self):
#     invoice = PrefixedInvoiceCustomerYearN(customer=customer)
#     invoice.save()

#     self.assertEqual(invoice.id_field, f"{PREFIX}{CUSTOMER_YEAR}-01")
