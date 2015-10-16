# -*- coding: utf-8 -*-
"""
Define the database model to know if a given Event/Eventlog
has been sent to a given social network
"""

from django.db import models


class Event(models.Model):

    event = models.ForeignKey('backoffice.Event')
    name = models.CharField(max_length=10)
    sn_id = models.CharField(max_length=30)

    class Meta:
        unique_together = ('event', 'name')


class EventLog(models.Model):

    eventlog = models.ForeignKey('backoffice.EventLog')
    name = models.CharField(max_length=10)
    sn_id = models.CharField(max_length=30)

    class Meta:
        unique_together = ('eventlog', 'name')
