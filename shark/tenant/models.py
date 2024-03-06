from django.db import models

from shark.base.models import BaseModel
from shark.billing.models import InvoiceTemplate
from shark.billing.utils.fake_invoice import FakeInvoiceTemplate
from shark.utils.fields import AddressField


class Tenant(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    address = AddressField()

    @property
    def default_invoice_template(self) -> InvoiceTemplate | None:
        return (
            self.invoicetemplate_set.filter(is_default=True).first()
            # FakeInvoiceTemplate is an empty InvoiceTemplate
            # without PK and FK relations
            or FakeInvoiceTemplate()
        )

    def __str__(self):
        return self.name
