# Generated by Django 5.0.7 on 2025-04-02 11:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("billing", "0002_initial"),
        ("tenant", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoicetemplate",
            name="tenant",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                to="tenant.tenant",
            ),
        ),
        migrations.AddField(
            model_name="invoice",
            name="template",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="billing.invoicetemplate",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="invoice",
            unique_together={("customer", "number")},
        ),
    ]
