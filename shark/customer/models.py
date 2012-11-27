from django.db import models


class BaseCustomer(models.Model):
    id = models.CharField(max_length=20, primary_key=True)

    class Meta:
        abstract = True


class Customer(BaseCustomer):
    pass
