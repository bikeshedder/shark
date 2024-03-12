from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from shark.base.models import BaseModel, BillableMixin, TaggableMixin, TenantMixin
from shark.id_generators.fields import IdField
from shark.utils.fields import AddressField, LanguageField


class Customer(BaseModel, BillableMixin, TaggableMixin, TenantMixin):
    name = models.CharField(max_length=50)
    number = IdField(type="customer", editable=False)

    # Language to be used when communicating with the customer. This
    # field is mainly used to determine which language to use when
    # generating invoices and email messages.
    language = LanguageField(_("language"), blank=True)

    class InvoiceDispatchType(models.TextChoices):
        EMAIL = "email", _("via email")
        MAIL = "mail", _("via mail")

    invoice_dispatch_type = models.CharField(
        max_length=20,
        choices=InvoiceDispatchType,
        default=InvoiceDispatchType.EMAIL,
        verbose_name=_("Invoice dispatch type"),
    )

    class PaymentType(models.TextChoices):
        INVOICE = "invoice", _("Invoice")
        DIRECT_DEBIT = "direct_debit", _("Direct debit")

    payment_type = models.CharField(
        max_length=20,
        choices=PaymentType,
        default=PaymentType.INVOICE,
        verbose_name=_("Payment Type"),
    )

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

    @property
    def vat_required(self):
        # VAT for invoices is required if customer...
        # ...lives in Germany
        # ...lives in the EU and does not have a VATIN
        return self.country.id == "DE" or (self.country.eu and not self.vatin)

    @property
    def billing_address(self) -> AddressField:
        return self.address_set.get(billing_address=True).address

    # Grappelli autocomplete
    @staticmethod
    def autocomplete_search_fields():
        return (
            "id__iexact",
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
