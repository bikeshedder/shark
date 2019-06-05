# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models, migrations
import django_countries.fields
import localflavor.generic.models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0001_initial'),
        ('documents', '0001_initial'),
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DirectDebitBatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, verbose_name='UUID')),
                ('creditor_id', models.CharField(default=b'', max_length=20, verbose_name='creditor id')),
                ('creditor_name', models.CharField(default=b'', max_length=70, verbose_name='creditor name')),
                ('creditor_country', models.CharField(default=b'DE', max_length=2, verbose_name='creditor country')),
                ('creditor_iban', localflavor.generic.models.IBANField(default=b'', max_length=34)),
                ('creditor_bic', localflavor.generic.models.BICField(default=b'', max_length=11, verbose_name='creditor BIC')),
                ('due_date', models.DateTimeField(help_text='Must be min. 5 TARGET dates in the future for the first transaction and 2 target days in the future for recurring transactions.', verbose_name='due date')),
                ('mandate_type', models.CharField(max_length=4, verbose_name='mandate type', choices=[(b'CORE', b'CORE'), (b'COR1', b'COR1'), (b'B2B', b'B2B')])),
                ('sequence_type', models.CharField(max_length=4, verbose_name='sequence type', choices=[(b'FRST', b'FRST'), (b'RCUR', b'RCUR')])),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('executed', models.DateTimeField(verbose_name='executed')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DirectDebitMandate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reference', models.CharField(unique=True, max_length=35, verbose_name='mandate reference', blank=True)),
                ('name', models.CharField(max_length=100)),
                ('street', models.CharField(max_length=100)),
                ('postal_code', models.CharField(max_length=20)),
                ('city', models.CharField(max_length=100)),
                ('country', django_countries.fields.CountryField(default=b'DE', max_length=2)),
                ('iban', localflavor.generic.models.IBANField(help_text=b'International Bank Account Number', max_length=34)),
                ('bic', localflavor.generic.models.BICField(help_text=b'Bank Identifier Code', max_length=11, verbose_name=b'BIC')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('signed', models.DateField(null=True, blank=True)),
                ('revoked', models.DateField(null=True, verbose_name='revoked', blank=True)),
                ('last_used', models.DateField(null=True, verbose_name='last_used', blank=True)),
                ('type', models.CharField(max_length=4, choices=[(b'CORE', b'CORE'), (b'COR1', b'COR1'), (b'B2B', b'B2B')])),
                ('customer', models.ForeignKey(related_name='direct_debit_mandate_set', verbose_name='customer', to='customer.Customer', on_delete=models.CASCADE)),
                ('document', models.ForeignKey(verbose_name='signed document', blank=True, to='documents.Document', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'SEPA direct debit mandate',
                'verbose_name_plural': 'SEPA direct debit mandates',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DirectDebitTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reference', models.CharField(max_length=140)),
                ('amount', models.DecimalField(verbose_name='amount', max_digits=11, decimal_places=2)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('batch', models.ForeignKey(verbose_name='SEPA DD batch', to='sepa.DirectDebitBatch', on_delete=models.CASCADE)),
                ('customer', models.ForeignKey(related_name='direct_debit_transaction_set', verbose_name='customer', to='customer.Customer', on_delete=models.CASCADE)),
                ('invoice', models.ForeignKey(verbose_name='invoice', blank=True, to='billing.Invoice', null=True, on_delete=models.CASCADE)),
                ('mandate', models.ForeignKey(verbose_name=b'SEPA DD mandate', to='sepa.DirectDebitMandate', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
