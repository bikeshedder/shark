from django.conf import settings
from django.db import models
from django.utils.functional import curry
from django.utils.translation import ugettext_lazy as _


class AddressField(models.TextField):

    def contribute_to_class(self, cls, name):
        super(AddressField, self).contribute_to_class(cls, name)
        getter = curry(self._get_FIELD_lines)
        setter = curry(self._set_FIELD_lines)
        cls.add_to_class('get_%s_lines' % name, getter)
        cls.add_to_class('set_%s_lines' % name, setter)
        cls.add_to_class('%s_lines' % name, property(getter, setter))

    def _get_FIELD_lines(self, obj):
        return self.value_from_object(obj).split('\n')

    def _set_FIELD_lines(self, obj, value):
        setattr(obj, self.attname, '\n'.join(value))


class LanguageField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 5)
        kwargs.setdefault('choices', settings.LANGUAGES)
        kwargs.setdefault('help_text', _('This field will be automatically filled with the language of the customer. If no language for the customer is specified the default language (%s) will be used.' % settings.LANGUAGE_CODE))
        super(LanguageField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["choices"]
        del kwargs['help_text']
        if 'default' in kwargs:
            del kwargs["default"]
        return name, path, args, kwargs
