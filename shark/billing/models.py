# Allow look-ahead Type annotations
# Without this, the Type's class definition needs to come before its usage
# Obsolete with Python 4
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.contrib import admin
from django.db import models
from django.utils.formats import date_format
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from shark.base.models import BaseModel, ProxyManager, TenantMixin
from shark.id_generators import YearCustomerN
from shark.id_generators.fields import IdField
from shark.utils.fields import AddressField, LanguageField
from shark.utils.rounding import round_to_centi
from shark.utils.settings import get_settings_value

INVOICE_PAYMENT_TIMEFRAME = get_settings_value(
    "INVOICE.PAYMENT_TIMEFRAME", timedelta(days=14)
)


class Invoice(BaseModel):
    #
    # general
    #
    customer = models.ForeignKey(
        "customer.Customer", on_delete=models.CASCADE, verbose_name=_("Customer")
    )
    number = IdField(
        verbose_name=_("number"), generator=YearCustomerN(), editable=False
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
        if self.reminded_at is None:
            deadline = self.created_at.date() + INVOICE_PAYMENT_TIMEFRAME
        else:
            deadline = self.reminded_at + INVOICE_PAYMENT_TIMEFRAME
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
        c.items = [item.clone() for item in self.items]
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

    class Type(models.TextChoices):
        TimeItem = "time"
        ArticleItem = "article"

    type = models.CharField(max_length=10, choices=Type, default=Type.TimeItem)
    sku = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("SKU"),
        help_text=_("Stock-keeping unit (e.g. Article number)"),
    )

    position = models.PositiveSmallIntegerField(verbose_name=_("position"))
    text = models.CharField(max_length=200, verbose_name=_("description"))
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("1"),
        verbose_name=_("quantity"),
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("price")
    )
    discount = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=("discount"),
    )

    VAT_RATE_CHOICES = [
        (Decimal("0.19"), "19%"),
        (Decimal("0.07"), "7%"),
        (Decimal("0.00"), "0%"),
    ]

    vat_rate = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        verbose_name=("VAT rate"),
        choices=VAT_RATE_CHOICES,
        default=VAT_RATE_CHOICES[0][0],
    )

    class Meta:
        verbose_name = _("Item")
        verbose_name_plural = _("Items")
        ordering = ["position"]

    def __str__(self):
        return "#%d %s" % (self.position or 0, self.text)

    def clone(self):
        return InvoiceItem(
            invoice=self.invoice,
            position=self.position,
            quantity=self.quantity,
            sku=self.sku,
            text=self.text,
            price=self.price,
            discount=self.discount,
            vat_rate=self.vat_rate,
        )

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


class InvoiceTimeItem(InvoiceItem):
    objects = ProxyManager(InvoiceItem.Type.TimeItem)

    class Meta:
        proxy = True

    @property
    @admin.display(description=_("Billing period"))
    def period(self):
        if self.begin and self.end:
            begin = date_format(self.begin, "SHORT_DATE_FORMAT")
            end = (
                date_format(self.end, "SHORT_DATE_FORMAT")
                if self.end is not None
                else _("one-time")
            )
            return "%s – %s" % (begin, end)
        else:
            return None

    @property
    def date(self):
        return self.begin or self.end if bool(self.begin) != bool(self.end) else None


class InvoiceArticleItem(InvoiceItem):
    objects = ProxyManager(InvoiceItem.Type.ArticleItem)

    class Meta:
        proxy = True


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
