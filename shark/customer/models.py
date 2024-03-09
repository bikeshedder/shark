from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from shark.base.models import BaseModel, TaggableMixin, TenantMixin
from shark.id_generators import InitialAsNumber
from shark.id_generators.fields import IdField
from shark.utils.fields import AddressField, LanguageField
from shark.utils.settings import get_settings_value

CUSTOMER_TYPE_CHOICES = get_settings_value("CUSTOMER.TYPE_CHOICES")
CUSTOMER_TYPE_DEFAULT = get_settings_value("CUSTOMER.TYPE_DEFAULT")


class CustomerTypeField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 20)
        kwargs.setdefault("choices", CUSTOMER_TYPE_CHOICES)
        kwargs.setdefault("default", CUSTOMER_TYPE_DEFAULT)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["choices"]
        del kwargs["default"]
        return name, path, args, kwargs


class Customer(BaseModel, TaggableMixin, TenantMixin):
    number = IdField(generator=InitialAsNumber(), editable=False)
    # XXX add_unique constraint
    name = models.CharField(max_length=50)

    # Language to be used when communicating with the customer. This
    # field is mainly used to determine which language to use when
    # generating invoices and email messages.
    language = LanguageField(_("language"), blank=True)

    # rates when creating invoices
    hourly_rate = models.DecimalField(
        _("hourly rate"), max_digits=7, decimal_places=2, blank=True, null=True
    )
    daily_rate = models.DecimalField(
        _("daily rate"), max_digits=7, decimal_places=2, blank=True, null=True
    )

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
        return f"{self.number} - {self.name}"

    @property
    def active(self):
        # The customer active flag does not depend on anything but
        # the enabled flag.
        return self.enabled

    @property
    def vat_required(self):
        # VAT for invoices is required if customer...
        # ...lives in Germany
        # ...lives in the EU and does not have a VATIN
        return self.country.id == "DE" or (self.country.eu and not self.vatin)

    @property
    def billing_address(self) -> AddressField:
        return self.address_set.get(invoice_address=True).address

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
