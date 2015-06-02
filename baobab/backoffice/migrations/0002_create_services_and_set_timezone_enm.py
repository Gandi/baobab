# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytz

from django.db import models, migrations
from django.contrib.auth.models import User
from django.conf import settings


# XXX to avoid to import baobab.backoffice.models.Service
IAAS = 0
PAAS = 1
SITE = 2
API = 3
SSL = 4
DOMAIN = 5
EMAIL = 6
SERVICE_CHOICES = (
    (IAAS, 'IAAS'),
    (PAAS, 'PAAS'),
    (SITE, 'Site'),
    (API, 'API'),
    (SSL, 'SSL'),
    (DOMAIN, 'Domain'),
    (EMAIL, 'Email'),
)

def forwards(apps, schema_editor):
    Service = apps.get_model('backoffice', 'Service')
    TimeZoneEnum = apps.get_model('backoffice', 'TimeZoneEnum')

    # create service
    for name, description in SERVICE_CHOICES:
        Service.objects.create(name=name, description=description)

    # set timezone
    for timezone in pytz.common_timezones:
        TimeZoneEnum.objects.create(name=timezone)

    timezone_id = TimeZoneEnum.objects.get(name=settings.TIME_ZONE).id
    for user in User.objects.all():
        TimeZone.objects.create(
            user_id=user.id,
            timezone_id=timezone_id,
        )

class Migration(migrations.Migration):

    dependencies = [
        ('backoffice', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards),
    ]
