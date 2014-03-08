from datetime import date

from django.test import TestCase

from shark.customer.models import Customer
from shark.billing.models import Invoice
from shark.utils.id_generators import DaysSinceEpoch
from shark.utils.id_generators import YearCustomerN
from shark.utils.id_generators import CustomerYearN


class DaysSinceEpochTestCase(TestCase):

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


class YearCustomerNTestCase(TestCase):

    def test_next(self):
        customer = Customer.objects.create(number='JOHNDOE')
        gen = YearCustomerN()
        gen.model_class = Invoice
        gen.field_name = 'number'
        today = date.today()
        prefix = '{:>04d}-JOHNDOE'.format(today.year)
        invoice1 = Invoice(customer=customer)
        invoice1.number = gen.next(invoice1)
        invoice1.save()
        self.assertEqual('%s-01' % prefix, invoice1.number)
        invoice2 = Invoice(customer=customer)
        invoice2.number = gen.next(invoice2)
        invoice2.save()
        self.assertEqual('%s-02' % prefix, invoice2.number)

    def test_invoice(self):
        customer = Customer.objects.create(number='JANEDOE')
        invoice = Invoice.objects.create(customer=customer)
        today = date.today()
        prefix = '{:>04d}-JANEDOE'.format(today.year)
        self.assertEqual('%s-01' % prefix, invoice.number)


class CustomerYearNTestCase(TestCase):

    def test_next(self):
        customer = Customer.objects.create(number='JOHNDOE')
        gen = CustomerYearN()
        gen.model_class = Invoice
        gen.field_name = 'number'
        today = date.today()
        prefix = 'JOHNDOE-%04d' % today.year
        invoice1 = Invoice(customer=customer)
        invoice1.number = gen.next(invoice1)
        invoice1.save()
        self.assertEqual('%s-01' % prefix, invoice1.number)
        invoice2 = Invoice(customer=customer)
        invoice2.number = gen.next(invoice2)
        invoice2.save()
        self.assertEqual('%s-02' % prefix, invoice2.number)

    def test_next_year2_nosep2(self):
        customer = Customer.objects.create(number='JOHNDOE')
        gen = CustomerYearN(year_length=2, separator2='')
        gen.model_class = Invoice
        gen.field_name = 'number'
        today = date.today()
        prefix = 'JOHNDOE-%s' % (str(today.year)[-2:])
        invoice1 = Invoice(customer=customer)
        invoice1.number = gen.next(invoice1)
        invoice1.save()
        self.assertEqual('%s01' % prefix, invoice1.number)
        invoice2 = Invoice(customer=customer)
        invoice2.number = gen.next(invoice2)
        invoice2.save()
        self.assertEqual('%s02' % prefix, invoice2.number)
