from composite_field import CompositeField
from django.conf import settings
from django.db import models
from django.utils.html import format_html_join, mark_safe
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField


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
        def lines(self):
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
        def lines_html(self):
            return format_html_join(
                mark_safe("<br>"), "{}", ((line,) for line in self.lines)
            )


class LanguageField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 7)
        kwargs.setdefault("choices", settings.LANGUAGES)
        kwargs.setdefault(
            "help_text",
            _(
                "This field will be automatically filled with the language of the customer. If no language for the customer is specified the default language (%s) will be used."
                % settings.LANGUAGE_CODE
            ),
        )
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["choices"]
        del kwargs["help_text"]
        if "default" in kwargs:
            del kwargs["default"]
        return name, path, args, kwargs
