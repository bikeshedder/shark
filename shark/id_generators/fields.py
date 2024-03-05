from copy import copy
from functools import partial

from django.db import models


class IdField(models.CharField):
    def __init__(self, **kwargs):
        self.generator = kwargs.pop("generator", None)
        kwargs.setdefault("max_length", 32)
        if self.generator:
            if self.generator.max_length > kwargs["max_length"]:
                raise RuntimeError(
                    "The generator is capable of generating IDs exceeding the max_length of this field. Consider using a different generator class or setting a higher max_length value to this field."
                )
        kwargs.setdefault("blank", True)
        kwargs.setdefault("unique", True)
        super(IdField, self).__init__(**kwargs)

    def contribute_to_class(self, cls, name):
        super(IdField, self).contribute_to_class(cls, name)
        if self.generator:
            generator = copy(self.generator)
            if not generator.model_class_given:
                generator.model_class = cls
            if not generator.field_name_given:
                generator.field_name = name
            models.signals.pre_save.connect(
                partial(self._pre_save, generator=generator), sender=cls, weak=False
            )

    # Do not name this method 'pre_save' as it will otherwise be called without
    # the generator argument.
    def _pre_save(self, generator, sender, instance, *args, **kwargs):
        if getattr(instance, self.name, ""):
            # Do not create an ID for objects that already have a value set.
            return
        value = generator.next(instance=instance)
        setattr(instance, self.name, value)
