# -*- coding: utf-8 -*-
"""
Define the database model to translate the comment (Event/EventLog)
"""

from django.contrib.auth.models import User

from django.db import models
from django.db.utils import OperationalError

from baobab.backoffice.models import (Event as BackOfficeEvent,
                                      EventLog as BackOfficeEventLog)


class Lang(models.Model):

    name = models.CharField(max_length=200, unique=True)
    iso = models.CharField(max_length=5, unique=True)

    @classmethod
    def count(cls):
        """
        the count method is need to declare some admin form
        we need to be sure the call won't raise
        """
        try:
            return cls.objects.count()
        except OperationalError as err:
            if not err.message.startswith('no such table'):
                raise
        return 0

    def __unicode__(self):
        return self.name


class EventData(models.Model):

    event = models.ForeignKey('backoffice.Event', related_name='eventdatas')
    lang = models.ForeignKey('Lang', related_name='eventdatas')
    title = models.CharField(max_length=255,
                             help_text='A short description of the event')
    summary = models.TextField(null=True, blank=True, default=None)
    user = models.ForeignKey(User, related_name='eventdatas', null=True,
                             default=None)

    class Meta:
        unique_together = ('event', 'lang')


class EventLogData(models.Model):

    eventlog = models.ForeignKey('backoffice.EventLog',
                                 related_name='eventlogdatas')
    lang = models.ForeignKey('Lang', related_name='eventlogdatas')
    comment = models.TextField()
    user = models.ForeignKey(User, related_name='eventlogdatas', null=True,
                             default=None)

    class Meta:
        unique_together = ('eventlog', 'lang')


# XXX can't have twice the same model in the admin so the following
#     are just fake models classes to be able to have them twice

class Event(BackOfficeEvent):

    class Meta:
        proxy = True


class EventLog(BackOfficeEventLog):

    class Meta:
        proxy = True
