from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(
        _("created_at"), auto_now_add=True, editable=False
    )
    updated_at = models.DateTimeField(_("updated_at"), auto_now=True, editable=False)

    class Meta:
        abstract = True

    @property
    @admin.display(description=_("Created date"))
    def created_at_date(self):
        return self.created_at.date()


class TaggableMixin(models.Model):
    tags = TaggableManager(_("tags"), blank=True)

    class Meta:
        abstract = True


class TenantMixin(models.Model):
    tenant = models.ForeignKey(
        "tenant.Tenant", editable=False, on_delete=models.CASCADE
    )

    class Meta:
        abstract = True


class BillableMixin(models.Model):
    hourly_rate = models.DecimalField(
        _("hourly rate"), max_digits=7, decimal_places=2, blank=True, null=True
    )

    class Meta:
        abstract = True

    @property
    def rate(self):
        raise NotImplementedError()


class BaseModel(TimeStampMixin):
    class Meta:
        abstract = True


class ProxyManager(models.Manager):
    def __init__(self, type):
        super().__init__()
        self.type = type

    def get_queryset(self):
        return super().get_queryset().filter(type=self.type)
