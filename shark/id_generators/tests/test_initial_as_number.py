from django.db import models
from django.db.utils import IntegrityError
from django.test import TestCase

from .. import InitialAsNumber
from ..fields import IdField


class NumberCustomer(models.Model):
    id_field = IdField(generator=InitialAsNumber())
    name = models.CharField()


class PrefixedNumberCustomer(models.Model):
    id_field = IdField(generator=InitialAsNumber(prefix="TEST"))
    name = models.CharField()


class TestInitialNumberGenerator(TestCase):
    customer = None

    def setUp(self):
        global customer
        customer = NumberCustomer(name="Ambros")
        customer.save()

    def test_first(self):
        self.assertEqual(customer.id_field, "0101")

    def test_next(self):
        customer = NumberCustomer(name="Anton")
        customer.save()

        self.assertEqual(customer.id_field, "0102")

    def test_different_initial(self):
        customer = NumberCustomer(name="Berta")
        customer.save()

        self.assertEqual(customer.id_field, "0201")

    def test_uniqueness(self):
        with self.assertRaises(IntegrityError):
            NumberCustomer(id_field="0101").save()

    def test_prefix(self):
        customer = PrefixedNumberCustomer(name="Anna")
        customer.save()

        self.assertEqual(customer.id_field, "TEST0101")

    def test_no_pollution(self):
        PrefixedNumberCustomer(name="Ambros").save()

        customer = NumberCustomer(name="Anna")
        customer.save()

        self.assertEqual(customer.id_field, "0102")
