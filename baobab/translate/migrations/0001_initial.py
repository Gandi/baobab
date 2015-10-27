# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('backoffice', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EventData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text=b'A short description of the event', max_length=255)),
                ('summary', models.TextField(default=None, null=True, blank=True)),
                ('event', models.ForeignKey(related_name=b'eventdatas', to='backoffice.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventLogData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField()),
                ('eventlog', models.ForeignKey(related_name=b'eventlogdatas', to='backoffice.EventLog')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Lang',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('iso', models.CharField(unique=True, max_length=5)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='eventlogdata',
            name='lang',
            field=models.ForeignKey(related_name=b'eventlogdatas', to='translate.Lang'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventlogdata',
            name='user',
            field=models.ForeignKey(related_name=b'eventlogdatas', default=None, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='eventlogdata',
            unique_together=set([('eventlog', 'lang')]),
        ),
        migrations.AddField(
            model_name='eventdata',
            name='lang',
            field=models.ForeignKey(related_name=b'eventdatas', to='translate.Lang'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventdata',
            name='user',
            field=models.ForeignKey(related_name=b'eventdatas', default=None, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='eventdata',
            unique_together=set([('event', 'lang')]),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('backoffice.event',),
        ),
        migrations.CreateModel(
            name='EventLog',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('backoffice.eventlog',),
        ),
    ]
