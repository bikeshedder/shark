from django.utils import unittest

from shark.customer.models import Customer
from shark.utils.id_generators import DaysSinceEpoch


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
