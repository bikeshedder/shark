from composite_field import CompositeField
from django.conf import settings
from django.db import models
from django.utils.html import format_html_join
from django.utils.translation import gettext_lazy as _
from django_countries.fields import Country, CountryField


def get_address_fieldlist(prefix="address"):
    """
    Gets the composite_field's subfield names.

    By default, fields will have the `address_` prefix.
    Set new prefix or empty string to change this behavior.
    """
    fields = list(AddressField.subfields.keys())
    return [f"{prefix}_{field}" for field in fields] if prefix else fields


class AddressField(CompositeField):
    name = models.CharField(_("name"), max_length=100)
    address_addition_1 = models.CharField(
        _("address addition (1st row)"), max_length=100, blank=True
    )
    address_addition_2 = models.CharField(
        _("address addition (2nd row)"), max_length=100, blank=True
    )
    street = models.CharField(_("street"), max_length=100)
    street_number = models.CharField(_("street number"), max_length=20, blank=True)
    city = models.CharField(_("city"), max_length=100)
    postal_code = models.CharField(_("postal code"), max_length=10)
    state = models.CharField(max_length=100, blank=True)
    country = CountryField(_("country"))

    def __init__(self, **kwargs):
        blank = kwargs.pop("blank", False)
        super().__init__(**kwargs)
        if blank:
            self["name"].blank = blank
            self["street"].blank = blank
            self["city"].blank = blank
            self["postal_code"].blank = blank
            self["country"].blank = blank

    class Proxy(CompositeField.Proxy):
        @property
        def lines(self) -> list[str]:
            return [
                line
                for line in [
                    self.name,
                    self.address_addition_1,
                    self.address_addition_2,
                    f"{self.street} {self.street_number}".strip(),
                    f"{self.postal_code} {self.city}".strip(),
                    self.state,
                    self.country.name,
                ]
                if line
            ]

        @property
        def lines_short(self) -> list[str]:
            return [
                line
                for line in [
                    self.name,
                    f"{self.street} {self.street_number}".strip(),
                    f"{self.postal_code} {self.city}".strip(),
                    self.country.name,
                ]
                if line
            ]

        @property
        def lines_html(self) -> str:
            return format_html_join("", "<p>{}</p>", ((line,) for line in self.lines))


def get_language_from_country(country: Country):
    match country.code:
        case "DE" | "AT" | "CH":
            return "de"
        case _:
            return "en"


class LanguageField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 7)
        kwargs.setdefault("choices", settings.LANGUAGES)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["choices"]
        if "default" in kwargs:
            del kwargs["default"]
        return name, path, args, kwargs


EU_COUNTRIES = [
    "BE",
    "EL",
    "LT",
    "PT",
    "BG",
    "ES",
    "LU",
    "RO",
    "CZ",
    "FR",
    "HU",
    "SI",
    "DK",
    "HR",
    "MT",
    "SK",
    "DE",
    "IT",
    "NL",
    "FI",
    "EE",
    "CY",
    "AT",
    "SE",
    "IE",
    "LV",
    "PL",
]
