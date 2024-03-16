# Generated by Django 5.0.3 on 2024-03-16 08:31

from decimal import Decimal

import django_countries.fields
from django.db import migrations, models

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
                    "number",
                    shark.id_generators.fields.IdField(
                        blank=True,
                        editable=False,
                        max_length=32,
                        unique=True,
                        verbose_name="number",
                    ),
                ),
                (
                    "language",
                    shark.utils.fields.LanguageField(
                        max_length=7, verbose_name="language"
                    ),
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
                    "payment_type",
                    models.CharField(
                        choices=[
                            ("invoice", "Invoice"),
                            ("direct_debit", "Direct debit"),
                        ],
                        default="invoice",
                        max_length=20,
                        verbose_name="Payment Type",
                    ),
                ),
                ("sender_name", models.CharField(max_length=100, verbose_name="name")),
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
                    models.CharField(max_length=100, verbose_name="street"),
                ),
                (
                    "sender_street_number",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="street number"
                    ),
                ),
                ("sender_city", models.CharField(max_length=100, verbose_name="city")),
                (
                    "sender_postal_code",
                    models.CharField(max_length=10, verbose_name="postal code"),
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
                    models.CharField(max_length=100, verbose_name="name"),
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
                    models.CharField(max_length=100, verbose_name="street"),
                ),
                (
                    "recipient_street_number",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="street number"
                    ),
                ),
                (
                    "recipient_city",
                    models.CharField(max_length=100, verbose_name="city"),
                ),
                (
                    "recipient_postal_code",
                    models.CharField(max_length=10, verbose_name="postal code"),
                ),
                ("recipient_state", models.CharField(blank=True, max_length=100)),
                (
                    "recipient_country",
                    django_countries.fields.CountryField(
                        max_length=2, verbose_name="country"
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
                ("position", models.PositiveSmallIntegerField(verbose_name="position")),
                ("text", models.CharField(max_length=200, verbose_name="description")),
                (
                    "sku",
                    models.CharField(
                        blank=True,
                        help_text="Stock-keeping unit (e.g. Article number)",
                        max_length=20,
                        verbose_name="SKU",
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
                    "price",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="price"
                    ),
                ),
                (
                    "begin",
                    models.DateField(blank=True, null=True, verbose_name="begin"),
                ),
                ("end", models.DateField(blank=True, null=True, verbose_name="end")),
                (
                    "unit",
                    models.CharField(
                        choices=[("h", "Hours"), ("pc", "Pieces")], default="pc"
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
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=3,
                        verbose_name="VAT rate",
                    ),
                ),
            ],
            options={
                "verbose_name": "Item",
                "verbose_name_plural": "Items",
                "ordering": ["position"],
            },
        ),
        migrations.CreateModel(
            name="InvoiceTemplate",
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
                ("name", models.CharField(verbose_name="Name")),
                ("is_selected", models.BooleanField(default=False)),
                (
                    "first_page_bg",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="",
                        verbose_name="First invoice page bg",
                    ),
                ),
                (
                    "later_pages_bg",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="",
                        verbose_name="Later invoice pages bg",
                    ),
                ),
                ("terms", models.TextField(blank=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="FakeInvoice",
            fields=[],
            options={
                "managed": False,
                "proxy": True,
                "default_permissions": [],
            },
            bases=("billing.invoice",),
        ),
    ]
