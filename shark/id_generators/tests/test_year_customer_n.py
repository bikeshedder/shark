from datetime import date

from django.db import models
from django.db.utils import IntegrityError
from django.test import TestCase

from .. import YearCustomerN
from ..fields import IdField

CURRENT_YEAR = date.today().year
CUSTOMER_NUMBER = "10101"
PREFIX = "TEST"


class YearCustomer(models.Model):
    number = models.CharField()


class Invoice(models.Model):
    id_field = IdField(generator=YearCustomerN())
    customer = models.ForeignKey(YearCustomer, on_delete=models.CASCADE)


class PrefixedInvoice(models.Model):
    id_field = IdField(generator=YearCustomerN(prefix=PREFIX))
    customer = models.ForeignKey(YearCustomer, on_delete=models.CASCADE)


class TestYearCustomerNGenerator(TestCase):
    invoice = None
    customer = None

    def setUp(self):
        global invoice, customer
        customer = YearCustomer(number=CUSTOMER_NUMBER)
        customer.save()

        invoice = Invoice(customer=customer)
        invoice.save()

    def test_first(self):
        self.assertEqual(invoice.id_field, f"{CURRENT_YEAR}-{CUSTOMER_NUMBER}-01")

    def test_next(self):
        invoice = Invoice(customer=customer)
        invoice.save()

        self.assertEqual(invoice.id_field, f"{CURRENT_YEAR}-{CUSTOMER_NUMBER}-02")

    def test_different_customer(self):
        CUSTOMER_NUMBER_2 = "20202"
        customer = YearCustomer(number=CUSTOMER_NUMBER_2)
        customer.save()

        invoice = Invoice(customer=customer)
        invoice.save()

        self.assertEqual(invoice.id_field, f"{CURRENT_YEAR}-{CUSTOMER_NUMBER_2}-01")

    def test_uniqueness(self):
        with self.assertRaises(IntegrityError):
            Invoice(id_field=f"{CURRENT_YEAR}-{CUSTOMER_NUMBER}-01").save()

    def test_prefix(self):
        invoice = PrefixedInvoice(customer=customer)
        invoice.save()

        self.assertEqual(
            invoice.id_field, f"{PREFIX}{CURRENT_YEAR}-{CUSTOMER_NUMBER}-01"
        )

    def test_no_pollution(self):
        PrefixedInvoice(customer=customer).save()

        invoice = Invoice(customer=customer)
        invoice.save()

        self.assertEqual(invoice.id_field, f"{CURRENT_YEAR}-{CUSTOMER_NUMBER}-02")
