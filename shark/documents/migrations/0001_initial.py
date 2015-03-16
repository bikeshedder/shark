# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_hashedfilenamestorage.storage
import taggit.managers
import shark.utils.date


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='title')),
                ('date', models.DateField(default=shark.utils.date.today, help_text=b'Date as written on the document.', verbose_name='date')),
                ('file', models.FileField(upload_to=b'documents', storage=django_hashedfilenamestorage.storage.HashedFilenameFileSystemStorage(), verbose_name='file')),
                ('size', models.BigIntegerField(default=0, verbose_name='file size', editable=False)),
                ('mime_type', models.CharField(help_text='Auto detected from uploaded file', max_length=100, verbose_name='MIME type', blank=True)),
                ('original', models.CharField(help_text='Where does this document come from?', max_length=10, verbose_name='original', choices=[(b'email', 'email'), (b'download', 'download'), (b'mail', 'mail'), (b'fax', 'fax'), (b'receipt', 'receipt')])),
                ('comment', models.TextField(verbose_name='comment', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('received', models.DateField(default=shark.utils.date.today, help_text=b'Date when the document was received.', verbose_name='received')),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='tags')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
