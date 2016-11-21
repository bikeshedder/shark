# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers
import shark.utils.fields
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='hourly_rate',
            field=models.DecimalField(null=True, verbose_name='hourly rate', max_digits=7, decimal_places=2, blank=True),
        ),
    ]
