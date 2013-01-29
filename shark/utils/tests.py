from datetime import date

from django.utils import unittest

from shark.customer.models import Customer
from shark.billing.models import Invoice
from shark.utils.id_generators import DaysSinceEpoch
from shark.utils.id_generators import YearCustomerN


class DaysSinceEpochTestCase(unittest.TestCase):

    def test_next(self):
        gen = DaysSinceEpoch(Customer, 'number')
        customer = Customer.objects.create(number=gen.next())
        self.assertLess(customer.number, gen.next())

    def test_id_field(self):
        # first customer
        customer1 = Customer.objects.create()
        self.assertNotEqual(customer1.number, '')
        # second customer
        customer2 = Customer.objects.create()
        self.assertNotEqual(customer2.number, '')
        self.assertNotEqual(customer2.number, customer1.number)


class YearCustomerNTestCase(unittest.TestCase):

    def test_next(self):
        customer = Customer.objects.create(number='JOHNDOE')
        gen = YearCustomerN()
        gen.model_class = Invoice
        gen.field_name = 'number'
        today = date.today()
        prefix = '{:>04d}-JOHNDOE'.format(today.year)
        invoice1 = Invoice.objects.create(
                customer=customer,
                number=gen.next(instance=customer, today=today))
        self.assertEqual('%s-01' % prefix, invoice1.number)
        invoice2 = Invoice.objects.create(
                customer=customer,
                number=gen.next(instance=customer, today=today))
        self.assertEqual('%s-02' % prefix, invoice2.number)
