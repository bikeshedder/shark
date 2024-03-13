from composite_field import CompositeField
from django.db import models
from django.utils.translation import gettext_lazy as _
from localflavor.generic.models import BICField, IBANField


class AccountInformation(CompositeField):
    iban = IBANField("IBAN", help_text="International Bank Account Number")
    bic = BICField("BIC", help_text="Bank Identifier Code")
    bank_name = models.CharField(max_length=50, blank=True)

    def __init__(self, **kwargs):
        blank = kwargs.pop("blank", False)
        super().__init__(**kwargs)
        if blank:
            self["iban"].blank = blank
            self["bic"].blank = blank


def get_creditor_fieldlist(prefix="creditor"):
    """
    Gets the composite_field's subfield names.

    By default, fields will have the `address_` prefix.
    Set new prefix or empty string to change this behavior.
    """
    fields = list(CreditorInformation.subfields.keys())
    return [f"{prefix}_{field}" for field in fields] if prefix else fields


class CreditorInformation(CompositeField):
    id = models.CharField(_("creditor id"), max_length=20)
    name = models.CharField(_("creditor name"), max_length=70)
    country = models.CharField(_("creditor country"), max_length=2)
    iban = IBANField(_("creditor IBAN"))
    bic = BICField(_("creditor BIC"))

    def __init__(self, **kwargs):
        blank = kwargs.pop("blank", False)
        super().__init__(**kwargs)
        if blank:
            self["id"].blank = blank
            self["name"].blank = blank
            self["country"].blank = blank
            self["iban"].blank = blank
            self["bic"].blank = blank
