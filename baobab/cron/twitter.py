# -*- coding: utf-8 -*-
"""
to send the Event or EventLog to twitter
"""

from datetime import datetime
import sys
import pytz

from baobab.backoffice.models import Event, EventLog
from baobab.utils.social_network import Twitter


def cron_twitter():
    if not Twitter.is_configured():
        print 'Twitter is not configured'
        sys.exit(0)
    twitter = Twitter()
    filters = {
        'msg_id__isnull': True,
        'date_start__lte': datetime.now(pytz.timezone('UTC')),
        'date_end__isnull': True,
    }
    for event in Event.objects.filter(**filters).exclude(
            msg__isnull=True).exclude(msg__exact=''):
        event.msg_id = twitter.create(event.msg, event.id)
        event.save()
        print 'Send tweet for Event id: %s' % event.id
    filters = {
        'msg_id__isnull': True,
        'date__lte': datetime.now(pytz.timezone('UTC')),
    }
    for eventlog in EventLog.objects.filter(**filters).exclude(
            msg__isnull=True).exclude(msg__exact=''):
        eventlog.msg_id = twitter.create(eventlog.msg, eventlog.event_id)
        eventlog.save()
        print 'Send tweet for EventLog id: %s' % eventlog.id
