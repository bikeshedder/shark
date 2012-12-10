from django.db import models
from django.utils.translation import ugettext_lazy as _

from shark.customer.fields import AddressField
from shark.utils.id_generators import IdField, DaysSinceEpoch


class BaseCustomer(models.Model):
    number = IdField(DaysSinceEpoch())
    address = AddressField(_('address'))
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    class Meta:
        verbose_name = _('customer')
        verbose_name_plural = _('customers')
        abstract = True


class Customer(BaseCustomer):
    pass
