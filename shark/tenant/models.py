from django.contrib.auth import get_user_model
from django.db import models

from shark.auth.models import User
from shark.base.models import BaseModel, InvoiceOptionsMixin, TenantMixin
from shark.billing.models import InvoiceTemplate
from shark.billing.utils.fake_invoice import EmptyInvoiceTemplate
from shark.id_generators.utils import (
    CustomerNumberGenerators,
    InvoiceNumberGenerators,
    get_customer_generator,
    get_invoice_generator,
)
from shark.sepa.fields import CreditorInformation
from shark.utils.fields import AddressField
from shark.utils.importlib import import_object


class Tenant(BaseModel, InvoiceOptionsMixin):
    name = models.CharField(max_length=255, unique=True)
    address = AddressField()

    customer_number_generator = models.CharField(
        choices=CustomerNumberGenerators,
        default=CustomerNumberGenerators.INITIAL_AS_NUMBER,
    )
    invoice_number_generator = models.CharField(
        choices=InvoiceNumberGenerators, default=InvoiceNumberGenerators.CUSTOMER_YEAR_N
    )

    creditor = CreditorInformation(blank=True)

    def __str__(self):
        return self.name

    @property
    def selected_invoice_template(self) -> InvoiceTemplate:
        return (
            self.invoicetemplate_set.filter(is_selected=True).first()
            or EmptyInvoiceTemplate()
        )

    def get_customer_number_generator(self):
        # Dynamically import the generator class
        generator_class = get_customer_generator(self.customer_number_generator)
        return import_object(generator_class)()

    def get_invoice_number_generator(self):
        # Dynamically import the generator class
        generator_class = get_invoice_generator(self.invoice_number_generator)
        return import_object(generator_class)()


class TenantMember(BaseModel, TenantMixin):
    user: User = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    projects = models.ManyToManyField("project.Project", blank=True)

    class Role(models.TextChoices):
        ADMIN = "ADMIN"
        EMPLOYEE = "EMPLOYEE"
        CUSTOMER_REPRESENTATIVE = "CUST_REP"

    role = models.CharField(max_length=10, choices=Role)

    def __str__(self):
        return self.user.get_full_name() or self.user.email
