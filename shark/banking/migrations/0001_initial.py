# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='account name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entry_date', models.DateField(verbose_name='entry date')),
                ('value_date', models.DateField(verbose_name='value date')),
                ('text_key', models.CharField(max_length=100)),
                ('primanota', models.CharField(max_length=100)),
                ('account_holder', models.CharField(max_length=100)),
                ('account_number', models.CharField(max_length=100)),
                ('bank_code', models.CharField(max_length=100)),
                ('reference', models.TextField(max_length=100)),
                ('currency', models.CharField(default=b'EUR', max_length=3)),
                ('amount', models.DecimalField(max_digits=11, decimal_places=2)),
                ('debit_credit', models.CharField(max_length=2)),
                ('account', models.ForeignKey(to='banking.Account', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
