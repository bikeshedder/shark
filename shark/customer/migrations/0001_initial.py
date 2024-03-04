# Generated by Django 4.2.10 on 2024-03-04 08:39

import django.db.models.deletion
import django_countries.fields
import taggit.managers
from django.conf import settings
from django.db import migrations, models

import shark.utils.fields
import shark.utils.id_generators


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        (
            "taggit",
            "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="Customer",
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
                    shark.utils.id_generators.IdField(
                        blank=True, max_length=32, unique=True
                    ),
                ),
                ("name", models.CharField(max_length=50)),
                (
                    "language",
                    shark.utils.fields.LanguageField(
                        blank=True, max_length=7, verbose_name="language"
                    ),
                ),
                (
                    "hourly_rate",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=7,
                        null=True,
                        verbose_name="hourly rate",
                    ),
                ),
                (
                    "daily_rate",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=7,
                        null=True,
                        verbose_name="daily rate",
                    ),
                ),
                (
                    "invoice_dispatch_type",
                    models.CharField(
                        choices=[("email", "via email"), ("mail", "via mail")],
                        default="email",
                        max_length=20,
                        verbose_name="Invoice dispatch type",
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
                (
                    "vatin",
                    models.CharField(
                        blank=True,
                        help_text="Value added tax identification number",
                        max_length=14,
                        verbose_name="VATIN",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        blank=True,
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="tags",
                    ),
                ),
            ],
            options={
                "verbose_name": "customer",
                "verbose_name_plural": "customers",
            },
        ),
        migrations.CreateModel(
            name="CustomerNote",
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
                ("text", models.TextField()),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="customer.customer",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CustomerAddress",
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
                    "name",
                    models.CharField(blank=True, max_length=100, verbose_name="name"),
                ),
                (
                    "address_addition_1",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        verbose_name="address addition (1st row)",
                    ),
                ),
                (
                    "address_addition_2",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        verbose_name="address addition (2nd row)",
                    ),
                ),
                ("street", models.CharField(max_length=100, verbose_name="street")),
                (
                    "street_number",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="street number"
                    ),
                ),
                ("city", models.CharField(max_length=100, verbose_name="city")),
                (
                    "postal_code",
                    models.CharField(max_length=10, verbose_name="postal code"),
                ),
                ("state", models.CharField(blank=True, max_length=100)),
                (
                    "country",
                    django_countries.fields.CountryField(
                        max_length=2, verbose_name="country"
                    ),
                ),
                (
                    "sender_line",
                    models.CharField(blank=True, default="", max_length=100),
                ),
                ("invoice_address", models.BooleanField(default=False)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="address_set",
                        to="customer.customer",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
