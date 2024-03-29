from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from shark.base.models import BaseModel, BillableMixin, TenantMixin
from shark.utils.time import decimal_hours_to_time


class Project(BaseModel, BillableMixin, TenantMixin):
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

    @property
    def rate(self):
        return self.hourly_rate or self.customer.rate


class Task(BaseModel, BillableMixin):
    project = models.ForeignKey("project.Project", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    hours_expected = models.DecimalField(
        null=True, blank=True, max_digits=7, decimal_places=2
    )
    hours_actual = models.DecimalField(
        null=True, blank=True, max_digits=7, decimal_places=2
    )
    due_by = models.DateField(null=True, blank=True)
    completed_at = models.DateField(null=True, blank=True)

    invoice_item = models.OneToOneField(
        "billing.InvoiceItem", blank=True, null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name

    @property
    def rate(self):
        return self.hourly_rate or self.project.rate

    @property
    def time_expected(self):
        return decimal_hours_to_time(self.hours_expected or Decimal(0))

    @property
    def time_actual(self):
        return decimal_hours_to_time(self.hours_actual or Decimal(0))
