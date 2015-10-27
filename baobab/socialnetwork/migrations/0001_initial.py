# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backoffice', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=10)),
                ('sn_id', models.CharField(max_length=30)),
                ('event', models.ForeignKey(to='backoffice.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=10)),
                ('sn_id', models.CharField(max_length=30)),
                ('eventlog', models.ForeignKey(to='backoffice.EventLog')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='eventlog',
            unique_together=set([('eventlog', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('event', 'name')]),
        ),
    ]
