# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('customer', models.ForeignKey(verbose_name='customer', to='customer.Customer', on_delete=models.CASCADE)),
            ],
        ),
    ]
