from composite_field import CompositeField
from django.conf import settings
from django.db import models
from django.utils.functional import curry
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField


class OldAddressField(models.TextField):

    def contribute_to_class(self, cls, name):
        super().contribute_to_class(cls, name)
        getter = curry(self._get_FIELD_lines)
        setter = curry(self._set_FIELD_lines)
        cls.add_to_class('get_%s_lines' % name, getter)
        cls.add_to_class('set_%s_lines' % name, setter)
        cls.add_to_class('%s_lines' % name, property(getter, setter))

    def _get_FIELD_lines(self, obj):
        return self.value_from_object(obj).split('\n')

    def _set_FIELD_lines(self, obj, value):
        setattr(obj, self.attname, '\n'.join(value))


class AddressField(CompositeField):
    name = models.CharField(_('name'), max_length=100)
    address_addition_1 = models.CharField(_('address addition (1st row)'), max_length=100, blank=True)
    address_addition_2 = models.CharField(_('address addition (2nd row)'), max_length=100, blank=True)
    street = models.CharField(_('street'), max_length=100)
    city = models.CharField(_('city'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=10)
    state = models.CharField(max_length=100, blank=True)
    country = CountryField(_('country'))

    def __init__(self, **kwargs):
        blank = kwargs.pop('blank', False)
        super().__init__(**kwargs)
        if blank:
            self['name'].blank = blank
            self['street'].blank = blank
            self['city'].blank = blank
            self['postal_code'].blank = blank
            self['country'].blank = blank


class LanguageField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 5)
        kwargs.setdefault('choices', settings.LANGUAGES)
        kwargs.setdefault('help_text', _('This field will be automatically filled with the language of the customer. If no language for the customer is specified the default language (%s) will be used.' % settings.LANGUAGE_CODE))
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["choices"]
        del kwargs['help_text']
        if 'default' in kwargs:
            del kwargs["default"]
        return name, path, args, kwargs
