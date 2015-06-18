# -*- coding: utf-8 -*-
"""
Close an Event with no date_end set and the duration has passed
"""

from datetime import datetime
import pytz

from baobab.backoffice.models import Event


def cron_close_event():
    now = datetime.now(pytz.timezone('UTC'))
    filters = {
        'date_start__lte': now,
        'estimate_date_end__lte': now,
        'date_end__isnull': True,
    }
    for event in Event.objects.filter(**filters):
        event.date_end = event.estimate_date_end
        event.save()
        print 'End Event id: %i' % event.id
