# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import localflavor.generic.models
import shark.sepa.models


class Migration(migrations.Migration):

    dependencies = [
        ('sepa', '0002_directdebitmandate_bank_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directdebitbatch',
            name='creditor_bic',
            field=localflavor.generic.models.BICField(default=shark.sepa.models.get_default_creditor_bic, max_length=11, verbose_name='creditor BIC'),
        ),
        migrations.AlterField(
            model_name='directdebitbatch',
            name='creditor_country',
            field=models.CharField(default=shark.sepa.models.get_default_creditor_country, max_length=2, verbose_name='creditor country'),
        ),
        migrations.AlterField(
            model_name='directdebitbatch',
            name='creditor_iban',
            field=localflavor.generic.models.IBANField(default=shark.sepa.models.get_default_creditor_iban, max_length=34),
        ),
        migrations.AlterField(
            model_name='directdebitbatch',
            name='creditor_id',
            field=models.CharField(default=shark.sepa.models.get_default_creditor_id, max_length=20, verbose_name='creditor id'),
        ),
        migrations.AlterField(
            model_name='directdebitbatch',
            name='creditor_name',
            field=models.CharField(default=shark.sepa.models.get_default_creditor_name, max_length=70, verbose_name='creditor name'),
        ),
    ]
