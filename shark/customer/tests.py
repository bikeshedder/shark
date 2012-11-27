from django.utils import unittest

from shark.customer.models import Customer


class CustomerTestCase(unittest.TestCase):

    def test_get_address_lines(self):
        customer = Customer(address='foo\nbar')
        self.assertEquals(customer.get_address_lines(), ['foo', 'bar'])

    def test_set_address_lines(self):
        customer = Customer()
        customer.set_address_lines(['foo', 'bar'])
        self.assertEquals(customer.address, 'foo\nbar')

    def test_address_lines_property(self):
        customer = Customer(address_lines=['foo', 'bar'])
        self.assertEquals(customer.address_lines, ['foo', 'bar'])
        self.assertEquals(customer.address, 'foo\nbar')
