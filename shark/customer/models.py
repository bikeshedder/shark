from django.db import models

from shark.customer.fields import AddressField


class BaseCustomer(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    address = AddressField()

    class Meta:
        abstract = True


class Customer(BaseCustomer):
    pass
