# Generated by Django 2.2.2 on 2019-06-05 12:39

from django.db import migrations, models
import django.db.models.deletion
import shark.utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0001_initial'),
        ('customer', '0004_add_various_fields'),
        ('documents', '0003_thumbnails'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='original',
        ),
        migrations.AddField(
            model_name='document',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='customer.Customer', verbose_name='customer'),
        ),
        migrations.AddField(
            model_name='document',
            name='direction',
            field=models.CharField(choices=[('internal', 'internal'), ('inbound', 'inbound'), ('outbound', 'outbound')], default='inbound', max_length=10, verbose_name='direction'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='document',
            name='original_filename',
            field=models.TextField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='recipient',
            field=shark.utils.fields.OldAddressField(blank=True),
        ),
        migrations.AddField(
            model_name='document',
            name='sender',
            field=shark.utils.fields.OldAddressField(blank=True),
        ),
        migrations.AddField(
            model_name='document',
            name='source',
            field=models.CharField(blank=True, choices=[('email', 'email'), ('download', 'download'), ('mail', 'mail'), ('fax', 'fax'), ('receipt', 'receipt'), ('self', 'self')], help_text='Where does this document come from?', max_length=10, verbose_name='original'),
        ),
        migrations.AddField(
            model_name='document',
            name='type',
            field=models.CharField(choices=[('invoice', 'invoice'), ('payment_reminder', 'payment reminder'), ('bank_statement', 'bank statement'), ('quote', 'quote'), ('misc', 'miscellaneous'), ('sepa_dd_mandate', 'SEPA direct debit mandate')], default='invoice', max_length=20, verbose_name='direction'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='document',
            name='vendor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='vendor.Vendor', verbose_name='vendor'),
        ),
    ]
