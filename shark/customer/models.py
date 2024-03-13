from django.contrib.auth import get_user_model
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_countries.fields import Country

from shark.base.models import (
    BaseModel,
    BillableMixin,
    InvoiceOptionsMixin,
    TaggableMixin,
    TenantMixin,
)
from shark.id_generators.fields import IdField
from shark.sepa.fields import AccountInformation
from shark.utils.fields import EU_COUNTRIES, AddressField, LanguageField


class Customer(
    BaseModel, BillableMixin, TaggableMixin, TenantMixin, InvoiceOptionsMixin
):
    name = models.CharField(max_length=50)
    number = IdField(type="customer", editable=False)
    language = LanguageField(_("language"), blank=True)

    class PaymentType(models.TextChoices):
        INVOICE = "invoice", _("Invoice")
        DIRECT_DEBIT = "direct_debit", _("Direct debit")

    payment_type = models.CharField(
        max_length=20,
        choices=PaymentType,
        default=PaymentType.INVOICE,
        verbose_name=_("Payment Type"),
    )

    account = AccountInformation(blank=True)

    vatin = models.CharField(
        max_length=14,
        blank=True,
        verbose_name=_("VATIN"),
        help_text=_("Value added tax identification number"),
    )

    class Meta:
        verbose_name = _("customer")
        verbose_name_plural = _("customers")

    def __str__(self):
        return self.name

    @property
    def rate(self):
        return self.hourly_rate

    @cached_property
    def days_to_pay(self):
        return (
            self.payment_timeframe_days
            if self.payment_timeframe_days is not None
            else self.tenant.payment_timeframe_days
        )

    @property
    def vat_required(self):
        # VAT for invoices is required if customer...
        # ...lives in Germany
        # ...lives in the EU and does not have a VATIN
        country: Country = self.billing_address.country
        return country.code == "DE" or country.code in EU_COUNTRIES and not self.vatin

    @property
    def billing_address(self) -> AddressField | None:
        return self.address_set.get(billing_address=True).address

    # Grappelli autocomplete
    @staticmethod
    def autocomplete_search_fields():
        return (
            "number__icontains",
            "name__icontains",
        )


class CustomerNote(BaseModel):
    customer = models.ForeignKey("customer.Customer", on_delete=models.CASCADE)
    user = models.ForeignKey(
        get_user_model(), blank=True, null=True, on_delete=models.SET_NULL
    )
    text = models.TextField()


class CustomerAddress(BaseModel):
    customer = models.ForeignKey(
        "customer.Customer", on_delete=models.CASCADE, related_name="address_set"
    )
    address = AddressField()
    billing_address = models.BooleanField(default=False)

    @property
    def lines(self):
        return self.address.lines

    @property
    def lines_html(self):
        return self.address.lines_html
