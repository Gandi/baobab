# -*- coding: utf-8 -*-
"""
to send the Event or EventLog to each define social network
"""

from datetime import datetime, timedelta
import pytz

from django.db.models import Q

from baobab.backoffice.models import Event, EventLog
from baobab.socialnetwork import SocialNetworks


def cron_social_network():
    now = datetime.now(pytz.timezone('UTC'))
    sn = SocialNetworks()

    filters = Q(date_start__lte=now) & (
        Q(date_end__gte=now) | Q(date_end__isnull=True)
    )
    for event in Event.objects.filter(filters):
        sn.publish(event)

    deltat = now - timedelta(minutes=5)
    filters = Q(date__lte=now) & (
        Q(event__date_end__gte=deltat) | Q(event__date_end__isnull=True)
    )
    for eventlog in EventLog.objects.filter(filters):
        sn.publish(eventlog)
