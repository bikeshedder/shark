# Generated by Django 3.2.7 on 2021-09-04 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Vendor",
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
                ("slug", models.SlugField(max_length=20, unique=True)),
                ("name", models.CharField(max_length=50, unique=True)),
            ],
        ),
    ]
