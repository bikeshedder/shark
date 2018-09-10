# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=b'issue/attachment', verbose_name='file')),
                ('description', models.TextField(verbose_name='description', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('summary', models.CharField(help_text='A concise description of the problem limited to 200 characters.', max_length=200, verbose_name='summary')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('project', models.ForeignKey(verbose_name='project', to='project.Project', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'issue',
                'verbose_name_plural': 'issues',
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=10, verbose_name='type')),
                ('text', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('author', models.ForeignKey(verbose_name='author', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('issue', models.ForeignKey(verbose_name='note', to='issue.Issue', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('watcher', models.BooleanField(default=False)),
                ('reporter', models.BooleanField(default=False)),
                ('waiting', models.BooleanField(default=False)),
                ('group', models.ForeignKey(verbose_name='group', to='auth.Group', on_delete=models.CASCADE)),
                ('issue', models.ForeignKey(verbose_name='issue', to='issue.Issue', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'participant',
                'verbose_name_plural': 'participants',
            },
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('b_is_parent', models.BooleanField()),
                ('b_is_related', models.BooleanField()),
                ('b_is_duplicate', models.BooleanField()),
                ('type', models.CharField(max_length=10, verbose_name='type', choices=[(b'parent', 'parent'), (b'related', 'related'), (b'duplicate', 'duplicate')])),
                ('a', models.ForeignKey(related_name='related_b_set', to='issue.Issue', on_delete=models.CASCADE)),
                ('b', models.ForeignKey(related_name='related_a_set', to='issue.Issue', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'relation',
                'verbose_name_plural': 'relations',
            },
        ),
        migrations.AddField(
            model_name='attachment',
            name='note',
            field=models.ForeignKey(verbose_name='note', to='issue.Note', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='relation',
            unique_together=set([('a', 'b')]),
        ),
        migrations.AlterUniqueTogether(
            name='participant',
            unique_together=set([('issue', 'user'), ('issue', 'group')]),
        ),
    ]
