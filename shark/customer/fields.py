from django.db import models
from django.utils.functional import curry


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


