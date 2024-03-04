# Generated by Django 4.2.10 on 2024-03-04 17:06

from decimal import Decimal

import django_countries.fields
from django.db import migrations, models

import shark.billing.models
import shark.id_generators.fields
import shark.utils.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Invoice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created_at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="updated_at"),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("invoice", "Invoice"),
                            ("correction", "Correction of invoice"),
                        ],
                        default="invoice",
                        max_length=20,
                        verbose_name="type",
                    ),
                ),
                (
                    "number",
                    shark.id_generators.fields.IdField(
                        blank=True, max_length=32, unique=True, verbose_name="number"
                    ),
                ),
                (
                    "language",
                    shark.utils.fields.LanguageField(
                        blank=True, max_length=7, verbose_name="language"
                    ),
                ),
                (
                    "payment_type",
                    models.CharField(
                        choices=[
                            ("invoice", "Invoice"),
                            ("direct_debit", "Direct debit"),
                        ],
                        default="invoice",
                        help_text="Will be copied from customer's preferences automatically.",
                        max_length=20,
                        verbose_name="Payment Type",
                    ),
                ),
                (
                    "sender_name",
                    models.CharField(
                        blank=True,
                        default="settings.SHARK['INVOICE']['SENDER']['name']",
                        max_length=100,
                        verbose_name="name",
                    ),
                ),
                (
                    "sender_address_addition_1",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        verbose_name="address addition (1st row)",
                    ),
                ),
                (
                    "sender_address_addition_2",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        verbose_name="address addition (2nd row)",
                    ),
                ),
                (
                    "sender_street",
                    models.CharField(
                        default="settings.SHARK['INVOICE']['SENDER']['street']",
                        max_length=100,
                        verbose_name="street",
                    ),
                ),
                (
                    "sender_street_number",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="street number"
                    ),
                ),
                (
                    "sender_city",
                    models.CharField(
                        default="settings.SHARK['INVOICE']['SENDER']['city']",
                        max_length=100,
                        verbose_name="city",
                    ),
                ),
                (
                    "sender_postal_code",
                    models.CharField(
                        default="settings.SHARK['INVOICE']['SENDER']['postal_code']",
                        max_length=10,
                        verbose_name="postal code",
                    ),
                ),
                ("sender_state", models.CharField(blank=True, max_length=100)),
                (
                    "sender_country",
                    django_countries.fields.CountryField(
                        max_length=2, verbose_name="country"
                    ),
                ),
                (
                    "recipient_name",
                    models.CharField(blank=True, max_length=100, verbose_name="name"),
                ),
                (
                    "recipient_address_addition_1",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        verbose_name="address addition (1st row)",
                    ),
                ),
                (
                    "recipient_address_addition_2",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        verbose_name="address addition (2nd row)",
                    ),
                ),
                (
                    "recipient_street",
                    models.CharField(blank=True, max_length=100, verbose_name="street"),
                ),
                (
                    "recipient_street_number",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="street number"
                    ),
                ),
                (
                    "recipient_city",
                    models.CharField(blank=True, max_length=100, verbose_name="city"),
                ),
                (
                    "recipient_postal_code",
                    models.CharField(
                        blank=True, max_length=10, verbose_name="postal code"
                    ),
                ),
                ("recipient_state", models.CharField(blank=True, max_length=100)),
                (
                    "recipient_country",
                    django_countries.fields.CountryField(
                        blank=True, max_length=2, verbose_name="country"
                    ),
                ),
                (
                    "net",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=10,
                        verbose_name="net",
                    ),
                ),
                (
                    "gross",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=10,
                        verbose_name="gross",
                    ),
                ),
                (
                    "reminded_at",
                    models.DateField(blank=True, null=True, verbose_name="Reminded"),
                ),
                (
                    "paid_at",
                    models.DateField(blank=True, null=True, verbose_name="Paid"),
                ),
            ],
            options={
                "verbose_name": "Invoice",
                "verbose_name_plural": "Invoices",
                "db_table": "billing_invoice",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="InvoiceItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("item", "Item"), ("title", "Title")],
                        default="item",
                        max_length=10,
                    ),
                ),
                (
                    "position",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="position"
                    ),
                ),
                (
                    "quantity",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("1"),
                        max_digits=10,
                        verbose_name="quantity",
                    ),
                ),
                (
                    "sku",
                    models.CharField(
                        blank=True,
                        help_text="Stock-keeping unit (e.g. Article number)",
                        max_length=20,
                        verbose_name="SKU",
                    ),
                ),
                ("text", models.CharField(max_length=200, verbose_name="description")),
                (
                    "begin",
                    models.DateField(blank=True, null=True, verbose_name="begin"),
                ),
                ("end", models.DateField(blank=True, null=True, verbose_name="end")),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="price"
                    ),
                ),
                (
                    "unit",
                    shark.billing.models.UnitField(
                        blank=True, max_length=10, verbose_name="unit"
                    ),
                ),
                (
                    "discount",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=3,
                        verbose_name="discount",
                    ),
                ),
                (
                    "vat_rate",
                    shark.billing.models.VatRateField(
                        decimal_places=2, max_digits=3, verbose_name="VAT rate"
                    ),
                ),
            ],
            options={
                "verbose_name": "Item",
                "verbose_name_plural": "Items",
                "db_table": "billing_invoice_item",
                "ordering": ("position",),
            },
        ),
    ]
