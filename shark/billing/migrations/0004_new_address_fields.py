# Generated by Django 2.2.2 on 2019-06-05 15:21

from django.db import migrations, models
import django_countries.fields
import shark.utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_meta_changes'),
    ]

    operations = [
        migrations.RenameField(
            model_name='invoice',
            old_name='recipient',
            new_name='old_recipient',
        ),
        migrations.AlterField(
            model_name='invoice',
            name='old_recipient',
            field=shark.utils.fields.OldAddressField(blank=True, db_column='recipient', help_text='This field will be automatically filled with the address of the customer.'),
        ),
        migrations.RenameField(
            model_name='invoice',
            old_name='sender',
            new_name='old_sender',
        ),
        migrations.AlterField(
            model_name='invoice',
            name='old_sender',
            field=shark.utils.fields.OldAddressField(blank=True, db_column='sender'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='recipient_address_addition_1',
            field=models.CharField(blank=True, max_length=100, verbose_name='address addition (1st row)'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='recipient_address_addition_2',
            field=models.CharField(blank=True, max_length=100, verbose_name='address addition (2nd row)'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='recipient_city',
            field=models.CharField(blank=True, max_length=100, verbose_name='city'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='recipient_country',
            field=django_countries.fields.CountryField(blank=True, max_length=2, verbose_name='country'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='recipient_name',
            field=models.CharField(blank=True, max_length=100, verbose_name='name'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='recipient_postal_code',
            field=models.CharField(blank=True, max_length=10, verbose_name='postal code'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='recipient_state',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='invoice',
            name='recipient_street',
            field=models.CharField(blank=True, max_length=100, verbose_name='street'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='sender_address_addition_1',
            field=models.CharField(blank=True, max_length=100, verbose_name='address addition (1st row)'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='sender_address_addition_2',
            field=models.CharField(blank=True, max_length=100, verbose_name='address addition (2nd row)'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='sender_city',
            field=models.CharField(default='', max_length=100, verbose_name='city'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='sender_country',
            field=django_countries.fields.CountryField(default='', max_length=2, verbose_name='country'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoice',
            name='sender_name',
            field=models.CharField(default='', max_length=100, verbose_name='name'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='sender_postal_code',
            field=models.CharField(default='', max_length=10, verbose_name='postal code'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='sender_state',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='invoice',
            name='sender_street',
            field=models.CharField(default='', max_length=100, verbose_name='street'),
        ),
    ]
