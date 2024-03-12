from django.db import models


class IdField(models.CharField):
    def __init__(self, type: str = None, **kwargs):
        self.generator_type = type
        kwargs.setdefault("max_length", 32)
        kwargs.setdefault("blank", True)
        kwargs.setdefault("unique", True)
        super().__init__(**kwargs)

    def contribute_to_class(self, cls, name):
        super().contribute_to_class(cls, name)
        self.model_class = cls
        self.field_name = name
        models.signals.pre_save.connect(self._generate, sender=cls, weak=False)

    def _generate(self, instance, *args, **kwargs):
        if getattr(instance, self.name, ""):
            # Do not create an ID for objects that already have a value set.
            return

        if self.generator_type == "customer":
            generator = instance.tenant.get_customer_number_generator()
        elif self.generator_type == "invoice":
            generator = instance.customer.tenant.get_invoice_number_generator()
        else:
            raise Exception("Cannot generate ID, no generator Type provided.")

        if not generator.model_class_given:
            generator.model_class = self.model_class
        if not generator.field_name_given:
            generator.field_name = self.field_name

        value = generator.next(instance=instance)
        setattr(instance, self.name, value)
