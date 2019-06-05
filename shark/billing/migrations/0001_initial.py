# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from decimal import Decimal
import shark.utils.fields
import shark.utils.id_generators


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(default=b'invoice', max_length=20, choices=[(b'invoice', 'Invoice'), (b'correction', 'Correction of invoice')])),
                ('number', shark.utils.id_generators.IdField(unique=True, max_length=32, blank=True)),
                ('language', shark.utils.fields.LanguageField(blank=True, help_text='This field will be automatically filled with the language of the customer. If no language for the customer is specified the default language (en-us) will be used.', max_length=5, choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')])),
                ('sender', shark.utils.fields.OldAddressField(default=b"settings.SHARK['INVOICE']['SENDER']", blank=True)),
                ('recipient', shark.utils.fields.OldAddressField(help_text='This field will be automatically filled with the address of the customer.', blank=True)),
                ('net', models.DecimalField(default=Decimal('0.00'), verbose_name='net', max_digits=10, decimal_places=2)),
                ('gross', models.DecimalField(default=Decimal('0.00'), verbose_name='gross', max_digits=10, decimal_places=2)),
                ('created', models.DateField(default=datetime.date.today, verbose_name='Created')),
                ('reminded', models.DateField(null=True, verbose_name='Reminded', blank=True)),
                ('paid', models.DateField(null=True, verbose_name='Paid', blank=True)),
                ('customer', models.ForeignKey(verbose_name='Customer', to='customer.Customer', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('-created',),
                'db_table': 'billing_invoice',
                'verbose_name': 'Invoice',
                'verbose_name_plural': 'Invoices',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.PositiveIntegerField(null=True, verbose_name='position', blank=True)),
                ('quantity', models.DecimalField(default=Decimal('1'), verbose_name='quantity', max_digits=10, decimal_places=2)),
                ('sku', models.CharField(help_text='Stock-keeping unit (e.g. Article number)', max_length=20, verbose_name='SKU', blank=True)),
                ('text', models.CharField(max_length=200, verbose_name='description')),
                ('begin', models.DateField(null=True, verbose_name='begin', blank=True)),
                ('end', models.DateField(null=True, verbose_name='end', blank=True)),
                ('price', models.DecimalField(verbose_name='price', max_digits=10, decimal_places=2)),
                ('unit', models.CharField(blank=True, max_length=10, verbose_name='unit', choices=[(b's', 'second [s]'), (b'min', 'minute [min]'), (b'h', 'hour [h]'), (b'd', 'day [d]'), (b'w', 'week [w]'), (b'm', 'month [m]'), (b'a', 'year [a]')])),
                ('discount', models.DecimalField(default=Decimal('0.00'), verbose_name=b'discount', max_digits=3, decimal_places=2)),
                ('vat_rate', models.DecimalField(verbose_name=b'VAT rate', max_digits=3, decimal_places=2, choices=[(Decimal('0.19'), '19%'), (Decimal('0.07'), '7%'), (Decimal('0.00'), '0%% (tax free)')])),
                ('customer', models.ForeignKey(verbose_name='customer', to='customer.Customer', on_delete=models.CASCADE)),
                ('invoice', models.ForeignKey(related_name='item_set', verbose_name='invoice', blank=True, to='billing.Invoice', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('position',),
                'db_table': 'billing_invoice_item',
                'verbose_name': 'Item',
                'verbose_name_plural': 'Items',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='invoiceitem',
            unique_together=set([('invoice', 'position')]),
        ),
        migrations.AlterUniqueTogether(
            name='invoice',
            unique_together=set([('customer', 'number')]),
        ),
    ]
