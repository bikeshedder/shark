from django.db import models
from django.utils.translation import ugettext_lazy as _


class Project(models.Model):
    name = models.CharField(_('name'), max_length=100)
    customer = models.ForeignKey('customer.Customer', verbose_name=_('customer'), on_delete=models.CASCADE)
    active = models.BooleanField(_('active'), default=True)

    def __str__(self):
        return self.name
