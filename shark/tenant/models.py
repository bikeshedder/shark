from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify

from shark.auth.models import User
from shark.base.models import BaseModel, InvoiceOptionsMixin, TenantMixin
from shark.id_generators.utils import (
    CustomerNumberGenerators,
    InvoiceNumberGenerators,
    get_customer_generator,
    get_invoice_generator,
)
from shark.sepa.fields import CreditorInformation
from shark.utils.fields import AddressField
from shark.utils.importlib import import_object

if TYPE_CHECKING:
    from shark.project.models import Project


class Tenant(BaseModel, InvoiceOptionsMixin):
    name = models.CharField(max_length=255, unique=True)
    address = AddressField()
    slug = models.SlugField(unique=True)

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

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_customer_number_generator(self):
        # Dynamically import the generator class
        generator_class = get_customer_generator(self.customer_number_generator)
        return import_object(generator_class)()

    def get_invoice_number_generator(self):
        # Dynamically import the generator class
        generator_class = get_invoice_generator(self.invoice_number_generator)
        return import_object(generator_class)()


class TenantMember(BaseModel, TenantMixin):
    user: "User" = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    projects: "models.ManyToManyField[Project]" = models.ManyToManyField(
        "project.Project", blank=True
    )

    class Role(models.TextChoices):
        ADMIN = "ADMIN"
        EMPLOYEE = "EMPLOYEE"
        CUSTOMER_REPRESENTATIVE = "CUST_REP"

    role = models.CharField(max_length=10, choices=Role)

    class Meta:
        db_table = "tenant_member"

    def __str__(self):
        return self.user.get_full_name() or self.user.email
