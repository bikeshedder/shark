from django.db import models
from django.utils.translation import gettext_lazy as _

from shark.base.models import BaseModel, TenantMixin


class Project(BaseModel, TenantMixin):
    name = models.CharField(_("name"), max_length=100)
    customer = models.ForeignKey(
        "customer.Customer",
        verbose_name=_("customer"),
        null=True,
        on_delete=models.SET_NULL,
    )
    active = models.BooleanField(_("active"), default=True)

    def __str__(self):
        return self.name
