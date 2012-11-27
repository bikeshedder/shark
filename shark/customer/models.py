from django.db import models
from django.utils.translation import ugettext_lazy as _

from shark.customer.fields import AddressField


class BaseCustomer(models.Model):
    id = models.CharField(_('id'), max_length=20, primary_key=True)
    address = AddressField(_('address'))
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    class Meta:
        verbose_name = _('customer')
        verbose_name_plural = _('customers')
        abstract = True


class Customer(BaseCustomer):
    pass
