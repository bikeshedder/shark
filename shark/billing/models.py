# Allow look-ahead Type annotations
# Without this, the Type's class definition needs to come before its usage
# Obsolete with Python 4
from __future__ import annotations

from copy import copy
from datetime import date, timedelta
from decimal import Decimal

from django.contrib import admin
from django.db import models
from django.utils.formats import date_format
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from shark.base.models import BaseModel, TenantMixin
from shark.id_generators.fields import IdField
from shark.utils.fields import AddressField, LanguageField
from shark.utils.rounding import round_to_centi


class Invoice(BaseModel):
    #
    # general
    #
    customer = models.ForeignKey(
        "customer.Customer", on_delete=models.CASCADE, verbose_name=_("Customer")
    )

    number = IdField(
        type="invoice",
        verbose_name=_("number"),
        editable=False,
    )
    language = LanguageField(_("language"))

    class Type(models.TextChoices):
        INVOICE = "invoice", _("Invoice")
        CORRECTION = "correction", _("Correction of invoice")

    type = models.CharField(
        _("type"), max_length=20, choices=Type, default=Type.INVOICE
    )

    class PaymentType(models.TextChoices):
        INVOICE = "invoice", _("Invoice")
        DIRECT_DEBIT = "direct_debit", _("Direct debit")

    payment_type = models.CharField(
        _("Payment Type"),
        max_length=20,
        choices=PaymentType,
        default=PaymentType.INVOICE,
    )

    #
    # address
    #
    sender = AddressField()
    recipient = AddressField()

    #
    # totals
    #
    net = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name=_("net")
    )
    gross = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("gross"),
    )

    #
    # status
    #
    reminded_at = models.DateField(blank=True, null=True, verbose_name=_("Reminded"))
    paid_at = models.DateField(blank=True, null=True, verbose_name=_("Paid"))

    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")
        unique_together = (("customer", "number"),)
        ordering = ("-created_at",)

    def __str__(self):
        return "%s %s" % (_("Invoice"), self.number)

    @property
    def recipient_lines(self):
        lines = self.recipient.lines
        if self.recipient.country == self.sender.country:
            del lines[-1]
        return lines

    @property
    def sender_lines(self):
        lines = self.sender.lines_short
        if self.recipient.country == self.sender.country:
            del lines[-1]
        return lines

    @property
    @admin.display(description=_("Okay"), boolean=True)
    def is_okay(self):
        if self.paid_at is not None:
            return True

        days_to_pay = self.customer.days_to_pay
        period_to_pay = timedelta(days=days_to_pay if days_to_pay is not None else 14)
        if self.reminded_at is None:
            deadline = self.created_at.date() + period_to_pay
        else:
            deadline = self.reminded_at + period_to_pay
        return date.today() <= deadline

    @cached_property
    def items(self) -> list[InvoiceItem]:
        return self.item_set.all()

    @property
    def correction(self):
        c = Invoice(
            customer=self.customer,
            number=self.number,
            language=self.language,
            sender=self.sender,
            recipient=self.recipient,
            created_at=self.created_at,
            type=self.Type.CORRECTION,
        )
        c.items = [copy(item) for item in self.items]
        for item in c.items:
            item.quantity = -item.quantity
        c.recalculate()
        return c

    def recalculate(self):
        self.net = sum(item.total for item in self.items)
        vat_amount = sum(item.amount for item in self.vat_items)
        self.gross = self.net + vat_amount

    @cached_property
    def vat_items(self):
        # create a dict which maps the vat rate to a list of items
        vat_dict = {}
        for item in self.items:
            if item.vat_rate == 0:
                continue
            vat_dict.setdefault(item.vat_rate, []).append(item)

        # sum up item per vat rate and create an ordered list of
        # (vat_rate, vat_amount) tuples.
        vat_list = []
        for vat_rate, items in vat_dict.items():
            amount = sum(item.total for item in items)
            vat_amount = round_to_centi(vat_rate * amount)
            vat_list.append((vat_rate, vat_amount))
        vat_list.sort()

        class VatItem(object):
            def __init__(self, rate, amount):
                self.rate = rate
                self.amount = amount

        return [VatItem(*t) for t in vat_list]


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        related_name="item_set",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("invoice"),
    )

    position = models.PositiveSmallIntegerField(verbose_name=_("position"))
    text = models.CharField(max_length=200, verbose_name=_("description"))
    sku = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("SKU"),
        help_text=_("Stock-keeping unit (e.g. Article number)"),
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("1"),
        verbose_name=_("quantity"),
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("price")
    )
    begin = models.DateField(_("begin"), blank=True, null=True)
    end = models.DateField(_("end"), blank=True, null=True)

    class Units(models.TextChoices):
        HOURS = "h"
        PIECES = "pc"

    unit = models.CharField(choices=Units, default=Units.PIECES)
    discount = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=("discount"),
    )
    vat_rate = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        verbose_name=("VAT rate"),
        default=Decimal("0.00"),
    )

    class Meta:
        verbose_name = _("Item")
        verbose_name_plural = _("Items")
        ordering = ["position"]

    def __str__(self):
        # Position value is 0-indexed => render value should be incremented
        return "#%d %s" % (self.position + 1, self.text)

    @property
    @admin.display(description=_("Subtotal"), boolean=True)
    def subtotal(self):
        return round_to_centi(self.quantity * self.price)

    @property
    def discount_percentage(self):
        return self.discount * 100

    @property
    def discount_amount(self):
        return round_to_centi(self.discount * self.subtotal)

    @property
    @admin.display(description=_("Sum of line"))
    def total(self):
        return self.subtotal - self.discount_amount

    @property
    @admin.display(description=_("Billing period"))
    def period(self):
        """
        Returns the time span between begin and end as a string
        "SHORT_DATE_BEGIN" - "SHORT_DATE_END"

        However, if BEGIN and END are the same, None is returned because
        "FROM X TO X" is not actually a period but a singular point in time
        """
        if self.begin and self.end:
            begin = date_format(self.begin, "SHORT_DATE_FORMAT")
            end = date_format(self.end, "SHORT_DATE_FORMAT")
            return "%s – %s" % (begin, end) if begin != end else None
        else:
            return None

    @property
    def date(self):
        return self.end or self.begin


class InvoiceTemplate(BaseModel, TenantMixin):
    name = models.CharField(_("Name"))
    is_selected = models.BooleanField(default=False)

    first_page_bg = models.FileField(_("First invoice page bg"), null=True, blank=True)
    later_pages_bg = models.FileField(
        _("Later invoice pages bg"), null=True, blank=True
    )

    terms = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_selected:
            InvoiceTemplate.objects.filter(tenant=self.tenant).exclude(
                pk=self.pk
            ).update(is_selected=False)

        super().save(*args, **kwargs)
