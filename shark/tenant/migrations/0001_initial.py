# Generated by Django 4.2.10 on 2024-03-05 09:48

import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tenant",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("address_name", models.CharField(max_length=100, verbose_name="name")),
                (
                    "address_address_addition_1",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        verbose_name="address addition (1st row)",
                    ),
                ),
                (
                    "address_address_addition_2",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        verbose_name="address addition (2nd row)",
                    ),
                ),
                (
                    "address_street",
                    models.CharField(max_length=100, verbose_name="street"),
                ),
                (
                    "address_street_number",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="street number"
                    ),
                ),
                ("address_city", models.CharField(max_length=100, verbose_name="city")),
                (
                    "address_postal_code",
                    models.CharField(max_length=10, verbose_name="postal code"),
                ),
                ("address_state", models.CharField(blank=True, max_length=100)),
                (
                    "address_country",
                    django_countries.fields.CountryField(
                        max_length=2, verbose_name="country"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
