from datetime import date

from django.db import IntegrityError
from django.test import TestCase

from shark.billing.models import Invoice
from shark.customer.models import Customer
from shark.tenant.models import Tenant

from ..utils import InvoiceNumberGenerators

CURRENT_YEAR = date.today().year
LAST_TWO_DIGITS = str(CURRENT_YEAR)[2:]
CURRENT_YEAR = int(LAST_TWO_DIGITS)


class TestCustomerYearNGenerator(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create(
            name="test-tenant",
            invoice_number_generator=InvoiceNumberGenerators.CUSTOMER_YEAR_N,
        )
        cls.customer = Customer.objects.create(tenant=cls.tenant, name="Anna")

    def test_first_and_next(self):
        invoice = Invoice.objects.create(customer=self.customer)
        self.assertEqual(invoice.number, f"{self.customer.number}-{CURRENT_YEAR}01")

        invoice2 = Invoice.objects.create(customer=self.customer)
        self.assertEqual(invoice2.number, f"{self.customer.number}-{CURRENT_YEAR}02")

    def test_different_customer(self):
        customer = Customer.objects.create(tenant=self.tenant, name="Bernd")
        invoice = Invoice.objects.create(customer=customer)
        self.assertEqual(invoice.number, f"{customer.number}-{CURRENT_YEAR}01")

    def test_uniqueness(self):
        invoice = Invoice.objects.create(customer=self.customer)
        with self.assertRaises(IntegrityError):
            Invoice.objects.create(number=invoice.number)


# def test_prefix(self):
#     invoice = PrefixedInvoiceCustomerYearN(customer=customer)
#     invoice.save()

#     self.assertEqual(invoice.id_field, f"{PREFIX}{CUSTOMER_YEAR}-01")
