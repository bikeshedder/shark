# Generated by Django 3.2.7 on 2021-09-04 17:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("customer", "0001_initial"),
        ("billing", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoiceitem",
            name="customer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="customer.customer",
                verbose_name="customer",
            ),
        ),
        migrations.AddField(
            model_name="invoiceitem",
            name="invoice",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="item_set",
                to="billing.invoice",
                verbose_name="invoice",
            ),
        ),
        migrations.AddField(
            model_name="invoice",
            name="customer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="customer.customer",
                verbose_name="Customer",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="invoiceitem",
            unique_together={("invoice", "position")},
        ),
        migrations.AlterUniqueTogether(
            name="invoice",
            unique_together={("customer", "number")},
        ),
    ]
