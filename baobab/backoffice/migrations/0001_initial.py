# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_update', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_start', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_end', models.DateTimeField(default=None, null=True, blank=True)),
                ('estimate_date_end', models.DateTimeField()),
                ('duration', models.PositiveIntegerField(help_text=b'Duration (in minutes)')),
                ('title', models.CharField(help_text=b'A short description of the event', max_length=255)),
                ('summary', models.TextField(default=None, null=True, blank=True)),
                ('category', models.PositiveSmallIntegerField(help_text=b'Type of the Event', choices=[(0, b'Maintenance'), (1, b'Incident')])),
                ('msg', models.CharField(default=None, max_length=255, null=True, verbose_name=b'Social Network', blank=True)),
            ],
            options={
                'ordering': ['id', 'pk'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('comment', models.TextField()),
                ('msg', models.CharField(max_length=255, null=True, verbose_name=b'Social Network', blank=True)),
                ('event', models.ForeignKey(related_name=b'eventlogs', to='backoffice.Event')),
                ('user', models.ForeignKey(related_name=b'eventlogs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.PositiveSmallIntegerField(help_text=b'name of the service', unique=True, choices=[(0, b'IAAS'), (1, b'PAAS'), (2, b'Site'), (3, b'API'), (4, b'SSL'), (5, b'Domain'), (6, b'Email')])),
                ('description', models.CharField(help_text=b'more information about the service', max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TimeZone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TimeZoneEnum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='timezone',
            name='timezone',
            field=models.ForeignKey(to='backoffice.TimeZoneEnum'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='timezone',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='services',
            field=models.ManyToManyField(related_name=b'events', to='backoffice.Service', blank=True),
            preserve_default=True,
        ),
    ]
