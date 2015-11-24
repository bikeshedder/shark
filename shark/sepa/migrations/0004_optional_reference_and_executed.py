# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sepa', '0003_default_values'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directdebitbatch',
            name='executed',
            field=models.DateTimeField(null=True, verbose_name='executed', blank=True),
        ),
        migrations.AlterField(
            model_name='directdebitmandate',
            name='reference',
            field=models.CharField(max_length=35, unique=True, null=True, verbose_name='mandate reference', blank=True),
        ),
    ]
