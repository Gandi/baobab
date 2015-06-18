# -*- coding: utf-8 -*-
"""
Define the database model for baobab
"""

from datetime import datetime, timedelta
import pytz

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

from baobab.utils.social_network import Twitter

from baobab.backoffice.modelmanager import EventManager


class Service(models.Model):
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
    name = models.PositiveSmallIntegerField(choices=SERVICE_CHOICES,
                                            unique=True,
                                            help_text='name of the service')
    description = models.CharField(
        max_length=100,
        help_text='more information about the service')

    # XXX this simulate an enum field like django does
    #     the third field is for the api schema
    SUNNY = 0
    CLOUDY = 1
    FOGGY = 2  # only use by the global status
    STORMY = 3
    STATUS_CHOICES = (
        (SUNNY, 'SUNNY', 'All services are up and running'),
        (CLOUDY, 'CLOUDY', 'A scheduled maintenance ongoing'),
        (FOGGY, 'FOGGY', 'Incident which are not impacting our services.'),
        (STORMY, 'STORMY', 'An incident ongoing'),
    )
    DICT_STATUS_CHOICES = dict(map(lambda x: (x[0], x[1]), STATUS_CHOICES))

    @property
    def status(self):
        date_end = Q(date_end__isnull=True) | Q(date_end__gt=now())
        if self.events.filter(
                date_end,
                date_start__lte=now(),
                category=Event.INCIDENT).exists():
            return Service.STORMY
        elif self.events.filter(
                date_end,
                date_start__lte=now(),
                category=Event.MAINTENANCE).exists():
            return Service.CLOUDY
        return Service.SUNNY

    def get_status_display(self):
        return Service.DICT_STATUS_CHOICES[self.status]

    def __unicode__(self):
        return '%s (%s)' % (self.get_name_display(), self.description)


class Event(models.Model):
    objects = EventManager()  # override the default manager

    # Used for <pubDate> in RSS Feed
    last_update = models.DateTimeField(default=now)

    date_start = models.DateTimeField(default=now)
    date_end = models.DateTimeField(null=True, blank=True, default=None)
    estimate_date_end = models.DateTimeField()
    duration = models.PositiveIntegerField(help_text='Duration (in minutes)')

    # XXX to remove at the next release
    title = models.CharField(max_length=255,
                             help_text='A short description of the event')

    # XXX to remove at the next release
    summary = models.TextField(null=True, blank=True, default=None)
    services = models.ManyToManyField('Service', related_name='events',
                                      blank=True)
    MAINTENANCE = 0
    INCIDENT = 1
    CATEGORY_CHOICES = (
        (MAINTENANCE, 'Maintenance'),
        (INCIDENT, 'Incident'),
    )
    category = models.PositiveSmallIntegerField(choices=CATEGORY_CHOICES,
                                                help_text='Type of the Event')
    msg_id = models.CharField(null=True, default=None, max_length=30)
    # XXX Twitter field for safety more than what's needed
    msg = models.CharField('Twitter', max_length=255, null=True, blank=True,
                           default=None)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id and self.date_end and self.date_end > now():
            # create an event with a date_end in future: need to be converted
            # to the estimate_date_end
            delta = self.date_end - self.date_start
            self.duration = delta.total_seconds() / 60
            self.date_end = None
        if self.date_end:
            delta = self.date_end - self.date_start
            self.duration = delta.total_seconds() / 60
            if not self.estimate_date_end or \
               self.date_start >= self.estimate_date_end:
                self.estimate_date_end = self.date_end
            if self.date_end <= now():
                if self.eventlogs.exists() and self.eventlogs.all()[0].date < self.date_end:
                    self.last_update = self.date_end
        else:
            delta = timedelta(minutes=self.duration)
            self.estimate_date_end = self.date_start + delta
        super(Event, self).save(*args, **kwargs)

    class Meta:
        # XXX avoid the admin to override the right order: see EventQuerySet
        ordering = ['id', 'pk']


class EventLog(models.Model):
    date = models.DateTimeField(default=now)

    # XXX to remove at the next release
    comment = models.TextField()

    event = models.ForeignKey('Event', related_name='eventlogs')
    user = models.ForeignKey(User, related_name='eventlogs')
    msg_id = models.CharField(null=True, default=None, max_length=30)
    # XXX Twitter field for safety more than what's needed
    msg = models.CharField('Twitter', max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        super(EventLog, self).save(*args, **kwargs)
        self.event.last_update = self.date
        self.event.save()

    class Meta:
        ordering = ['-date', ]


class TimeZoneEnum(models.Model):

    """
    this is an 'enum' with the possible value
    """
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class TimeZone(models.Model):

    """
    to be able to have the admin in the user's time-zone
    see `baobab.utils.set_current_timezone.TimezoneMiddleware`
    """
    user = models.OneToOneField(User)
    timezone = models.ForeignKey('TimeZoneEnum')

    def __unicode__(self):
        return self.timezone.name


@receiver(post_save, sender=User, dispatch_uid='OnUserCreate')
def on_user_create(instance, created, raw, **kwargs):
    """
    To set the default timezone to a new user
    """

    # no trigger when loading fixture
    # no trigger when updating a user
    if raw or not created:
        return

    TimeZone.objects.create(
        user_id=instance.id,
        timezone_id=TimeZoneEnum.objects.get(name=settings.TIME_ZONE).id,
    )


@receiver(post_save, sender=Event, dispatch_uid='OnEvent')
def on_event(instance, raw, **kwargs):
    """
    Send a Tweet on Tweeter
    """

    # no trigger when loading fixture
    # tweet if the message is not empty
    # do not re-tweet
    if raw or not instance.msg or instance.msg_id:
        return

    if instance.category == Event.MAINTENANCE and \
            instance.date_start > datetime.now(pytz.timezone('UTC')):
        return

    if Twitter.is_configured():
        msg_id = Twitter().create(instance.msg, instance.id)
        if msg_id:
            instance.msg_id = msg_id
            instance.save()


@receiver(post_save, sender=EventLog, dispatch_uid='OnEventLog')
def on_eventlog(instance, raw, **kwargs):
    """
    Send a Tweet on Tweeter
    """

    # no trigger when loading fixture
    # tweet if the message is not empty
    # do not re-tweet
    if raw or not instance.msg or instance.msg_id:
        return

    if instance.event.category == Event.MAINTENANCE and \
            instance.event.date_start > datetime.now(pytz.timezone('UTC')):
        return

    if Twitter.is_configured():
        msg_id = Twitter().create(instance.msg, instance.event_id)
        if msg_id:
            instance.msg_id = msg_id
            instance.save()
