# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers
import shark.utils.fields
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        ('customer', '0002_add_hourly_rate'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('address_addition', models.CharField(max_length=100, verbose_name='name')),
                ('street', models.CharField(max_length=100, verbose_name='street')),
                ('city', models.CharField(max_length=100, verbose_name='city')),
                ('postal_code', models.CharField(max_length=10, verbose_name='postal code')),
                ('country', django_countries.fields.CountryField(max_length=2, verbose_name='country')),
                ('invoice_address', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gender', models.CharField(blank=True, max_length=1, verbose_name='Gender', choices=[(b'M', 'Male'), (b'F', 'Female')])),
                ('title', models.CharField(blank=True, help_text='z.B. Herr, Frau, Dr., Prof.,...', max_length=20, verbose_name='Salutation', choices=[(b'Herr', b'Herr'), (b'Frau', b'Frau'), (b'Fr\xc3\xa4ulein', b'Fr\xc3\xa4ulein'), (b'Dr.', b'Dr.'), (b'Dr. Dr.', b'Dr. Dr.'), (b'Prof. Dr.', b'Prof. Dr.')])),
                ('first_name', models.CharField(max_length=20, verbose_name='First name', blank=True)),
                ('last_name', models.CharField(max_length=20, verbose_name='Last name', blank=True)),
                ('phone_number', models.CharField(max_length=50, blank=True)),
                ('mobile_number', models.CharField(max_length=50, blank=True)),
                ('fax_number', models.CharField(max_length=50, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='daily_rate',
            field=models.DecimalField(null=True, verbose_name='daily rate', max_digits=7, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='invoice_dispatch_type',
            field=models.CharField(default=b'email', max_length=20, verbose_name='Invoice dispatch type', choices=[(b'email', 'via email'), (b'fax', 'via FAX'), (b'mail', 'via mail')]),
        ),
        migrations.AddField(
            model_name='customer',
            name='payment_type',
            field=models.CharField(default=b'invoice', max_length=20, verbose_name='Payment Type', choices=[(b'invoice', 'Invoice'), (b'direct_debit', 'Direct debit')]),
        ),
        migrations.AddField(
            model_name='customer',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='customer',
            name='vatin',
            field=models.CharField(help_text='Value added tax identification number', max_length=14, verbose_name='VATIN', blank=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='language',
            field=shark.utils.fields.LanguageField(blank=True, max_length=5, verbose_name='language', choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')]),
        ),
        migrations.AddField(
            model_name='customercomment',
            name='customer',
            field=models.ForeignKey(to='customer.Customer', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='customeraddress',
            name='customer',
            field=models.ForeignKey(to='customer.Customer', on_delete=models.CASCADE),
        ),
    ]
