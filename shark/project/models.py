from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from shark.base.models import BaseModel, BillableMixin, TenantMixin
from shark.utils.time import decimal_hours_to_time

if TYPE_CHECKING:
    from shark.billing.models import InvoiceItem
    from shark.customer.models import Customer
    from shark.tenant.models import Member


class Project(BaseModel, BillableMixin, TenantMixin):
    name = models.CharField(_("name"), max_length=100)
    customer: "Customer" = models.ForeignKey(
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
        return self.hourly_rate or self.customer.hourly_rate


class ProjectDescription(BaseModel):
    project: Project = models.OneToOneField(Project, on_delete=models.CASCADE)
    repository = models.URLField(_("project repository"), blank=True)
    text = models.TextField(_("description"), blank=True)


class Task(BaseModel, BillableMixin):
    project: Project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    hours_expected = models.DecimalField(
        null=True, blank=True, max_digits=7, decimal_places=2
    )
    hours_actual = models.DecimalField(
        null=True, blank=True, max_digits=7, decimal_places=2
    )
    due_by = models.DateField(null=True, blank=True)
    completed_at = models.DateField(null=True, blank=True)
    invoice_item: "InvoiceItem" = models.OneToOneField(
        "billing.InvoiceItem", blank=True, null=True, on_delete=models.SET_NULL
    )
    assigned_to: "models.ManyToManyField[Member]" = models.ManyToManyField(
        "tenant.Member"
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


class TaskDescription(BaseModel):
    task: Task = models.OneToOneField(Task, on_delete=models.CASCADE)
    text = models.TextField(_("description"), blank=True)


class TaskTimeEntry(BaseModel):
    task: Task = models.ForeignKey(Task, null=True, on_delete=models.SET_NULL)
    employee: "Member" = models.ForeignKey(
        "tenant.Member", null=True, on_delete=models.SET_NULL
    )
    note = models.TextField(_("note"), blank=True)
    date = models.DateField(_("date"))
    duration = models.DecimalField(
        _("duration in hours"), max_digits=7, decimal_places=2
    )
