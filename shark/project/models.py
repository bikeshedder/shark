from django.db import models
from django.utils.translation import ugettext_lazy as _

from shark import get_model_name

CUSTOMER_MODEL = get_model_name('customer.Customer')


class Project(models.Model):
    name = models.CharField(_('name'), max_length=100)
    customer = models.ForeignKey(CUSTOMER_MODEL, verbose_name=_('customer'), on_delete=models.CASCADE)
    active = models.BooleanField(_('active'), default=True)

    def __str__(self):
        return self.name
