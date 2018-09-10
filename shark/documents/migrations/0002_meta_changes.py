# Generated by Django 2.1.1 on 2018-09-10 13:18

from django.db import migrations, models
import django_hashedfilenamestorage.storage
import shark.utils.date


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='date',
            field=models.DateField(default=shark.utils.date.today, help_text='Date as written on the document.', verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='document',
            name='file',
            field=models.FileField(storage=django_hashedfilenamestorage.storage.HashedFilenameFileSystemStorage(), upload_to='documents', verbose_name='file'),
        ),
        migrations.AlterField(
            model_name='document',
            name='original',
            field=models.CharField(blank=True, choices=[('email', 'email'), ('download', 'download'), ('mail', 'mail'), ('fax', 'fax'), ('receipt', 'receipt')], help_text='Where does this document come from?', max_length=10, verbose_name='original'),
        ),
        migrations.AlterField(
            model_name='document',
            name='received',
            field=models.DateField(default=shark.utils.date.today, help_text='Date when the document was received.', verbose_name='received'),
        ),
    ]
