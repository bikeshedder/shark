from django.db import IntegrityError
from django.test import TestCase

from shark.customer.models import Customer
from shark.tenant.models import Tenant

from ..utils import CustomerNumberGenerators


class TestInitialNumberGenerator(TestCase):
    customer = None

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create(
            name="test-tenant",
            invoice_number_generator=CustomerNumberGenerators.INITIAL_AS_NUMBER,
        )

    def test_first_and_next(self):
        customer = Customer.objects.create(tenant=self.tenant, name="Anna")
        self.assertEqual(customer.number, "0101")

        customer2 = Customer.objects.create(tenant=self.tenant, name="Anton")
        self.assertEqual(customer2.number, "0102")

    def test_different_initial(self):
        customer = Customer.objects.create(tenant=self.tenant, name="Bert")
        self.assertEqual(customer.number, "0201")

    def test_uniqueness(self):
        Customer.objects.create(tenant=self.tenant, name="Anna")
        with self.assertRaises(IntegrityError):
            Customer.objects.create(number="0101")

    def test_non_standard_character(self):
        customer = Customer.objects.create(tenant=self.tenant, name=" ")

        self.assertEqual(customer.number, "0001")

    # def test_prefix(self):
    #     customer = PrefixedNumberCustomer(name="Anna")
    #     customer.save()

    #     self.assertEqual(customer.id_field, "TEST0101")
