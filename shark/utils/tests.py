from django.utils import unittest

from shark.customer.models import Customer
from shark.utils.id_generators import DaysSinceEpoch


class DaysSinceEpochTestCase(unittest.TestCase):

    def test_next(self):
        gen = DaysSinceEpoch(Customer)
        customer = Customer.objects.create(id=gen.next())
        self.assertLess(customer.id, gen.next())
