import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from shark.base.models import BaseModel, TenantMixin
from shark.sepa.fields import (
    AccountInformation,
    CreditorInformation,
    get_creditor_fieldlist,
)

from . import sepaxml
from .utils import anonymize_iban


class DirectDebitMandate(BaseModel):
    customer = models.ForeignKey(
        "customer.Customer",
        on_delete=models.CASCADE,
        verbose_name=_("customer"),
    )
    reference = models.CharField(
        _("mandate reference"), max_length=35, unique=True, blank=True, null=True
    )
    name = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    country = CountryField(default="DE")
    account = AccountInformation(prefix="")
    signed_at = models.DateField(_("signed_at"), blank=True, null=True)
    revoked_at = models.DateField(_("revoked_at"), blank=True, null=True)
    last_used = models.DateField(_("last_used"), blank=True, null=True)

    class Type(models.TextChoices):
        CORE = "CORE", "CORE"
        COR1 = "COR1", "COR1"
        B2B = "B2B", "B2B"

    type = models.CharField(max_length=4, choices=Type)

    class Meta:
        verbose_name = _("SEPA direct debit mandate")
        verbose_name_plural = _("SEPA direct debit mandates")

    def __str__(self):
        return self.reference or "<no reference>"

    @property
    def address_lines(self):
        return [
            self.name,
            self.street,
            self.postal_code + " " + self.city,
            self.get_country_display(),
        ]

    @property
    def anonymized_iban(self):
        return anonymize_iban(self.iban)


class DirectDebitTransaction(BaseModel):
    customer = models.ForeignKey(
        "customer.Customer",
        on_delete=models.CASCADE,
        verbose_name=_("customer"),
    )
    mandate = models.ForeignKey(
        "sepa.DirectDebitMandate",
        verbose_name=_("SEPA DD mandate"),
        on_delete=models.CASCADE,
    )
    reference = models.CharField(max_length=140)
    amount = models.DecimalField(_("amount"), max_digits=11, decimal_places=2)
    invoice = models.ForeignKey(
        "billing.Invoice",
        verbose_name=_("invoice"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    batch = models.ForeignKey(
        "sepa.DirectDebitBatch",
        verbose_name=_("SEPA DD batch"),
        on_delete=models.CASCADE,
    )

    @classmethod
    def from_invoice(cls, invoice):
        mandate = (
            DirectDebitMandate.objects.filter(
                customer=invoice.customer, revoked_at=None
            )
            .order_by("-created_at")[:1]
            .get()
        )
        obj = cls(
            customer=invoice.customer,
            mandate=mandate,
            reference=invoice.number,
            amount=invoice.gross,
            invoice=invoice,
        )
        return obj


class DirectDebitBatch(BaseModel, TenantMixin):
    """
    This model is used to process multiple SEPA DD transactions
    together. This is typically achieved by generating a SEPA XML
    file.
    """

    uuid = models.UUIDField(_("UUID"), default=uuid.uuid4, editable=False)

    creditor = CreditorInformation()
    due_date = models.DateField(
        _("due date"),
        help_text=_(
            "Must be min. 5 TARGET dates in the future for the first transaction and 2 target days in the future for recurring transactions."
        ),
    )
    mandate_type = models.CharField(
        _("mandate type"), max_length=4, choices=DirectDebitMandate.Type
    )

    class SequenceType(models.TextChoices):
        FRST = "FRST", "FRST"
        RCUR = "RCUR", "RCUR"

    sequence_type = models.CharField(
        _("sequence type"), max_length=4, choices=SequenceType
    )
    executed_at = models.DateTimeField(_("executed_at"), blank=True, null=True)

    def save(self, *args, **kwargs):
        # Inherit creditor values from tenant
        for field in get_creditor_fieldlist():
            if not getattr(self, field, None):
                setattr(self, field, getattr(self.tenant, field))
        super().save(*args, **kwargs)

    @property
    def transactions(self):
        return list(self.directdebittransaction_set.all())

    def render_sepa_xml(self):
        """
        Create SEPA XML document according to ISO20222.
        """
        dd = sepaxml.DirectDebit(
            id=self.uuid.hex,
            creditor_id=self.creditor.id,
            creditor_name=self.creditor.name,
            creditor_country=self.creditor.country,
            creditor_iban=self.creditor.iban,
            creditor_bic=self.creditor.bic,
            due_date=self.due_date,
            mandate_type=self.mandate_type,
            sequence_type=self.sequence_type,
            transactions=[
                sepaxml.Transaction(
                    debitor_name=txn.mandate.name,
                    debitor_country=txn.mandate.country,
                    debitor_iban=txn.mandate.iban,
                    debitor_bic=txn.mandate.bic,
                    reference=settings.SHARK["SEPA"]["TRANSACTION_REFERENCE_PREFIX"]
                    + txn.reference,
                    amount=txn.amount,
                    mandate_id=txn.mandate.reference,
                    mandate_date=txn.mandate.signed_at,
                )
                for txn in self.directdebittransaction_set.all()
            ],
        )
        return dd.render_xml()
