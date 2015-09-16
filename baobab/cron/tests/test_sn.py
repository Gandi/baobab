# -*- coding: utf-8 -*-
import datetime

from django.utils.timezone import now as tz_now

from baobab.utils.test import TestCase
from baobab.backoffice.models import Event, EventLog
from baobab.socialnetwork.models import (Event as SnEvent,
                                         EventLog as SnEventLog)
from baobab.utils.mock import MockSN

from baobab.cron.socialnetwork import cron_social_network


class TestSN(TestCase):
    fixtures = ['db_user', 'db_backoffice']

    def _create_event(self, now, end=None):
        event = Event()
        event.date_start = now
        if not end:
            event.duration = 42
        event.date_end = end
        event.title = 'My Title'
        event.summary = ''
        event.category = Event.INCIDENT
        event.msg = 'a msg to publish'
        event.save()
        SnEvent.objects.all().delete()
        return event

    def test_01_event_not_started_with_end(self):
        now = tz_now().replace(microsecond=0) + datetime.timedelta(minutes=10)
        end = now + datetime.timedelta(minutes=10)
        event = self._create_event(now, end)
        cron_social_network()
        self.assertEqual(SnEvent.objects.count(), 0)

    def test_02_event_not_started_without_end(self):
        now = tz_now().replace(microsecond=0) + datetime.timedelta(minutes=10)
        event = self._create_event(now)
        cron_social_network()
        self.assertEqual(SnEvent.objects.count(), 0)

    def test_03_event_started_with_end(self):
        now = tz_now().replace(microsecond=0) - datetime.timedelta(minutes=10)
        end = now + datetime.timedelta(minutes=20)
        event = self._create_event(now, end)
        cron_social_network()
        self.assertEqual(SnEvent.objects.count(), 1)
        sn_event = SnEvent.objects.get(id=1)
        self.assertEqual(sn_event.event, event)
        self.assertEqual(sn_event.name, MockSN.name)
        self.assertEqual(sn_event.sn_id, '1')

    def test_04_event_started_without_end(self):
        now = tz_now().replace(microsecond=0) - datetime.timedelta(minutes=10)
        event = self._create_event(now)
        cron_social_network()
        self.assertEqual(SnEvent.objects.count(), 1)
        sn_event = SnEvent.objects.get(id=1)
        self.assertEqual(sn_event.event, event)
        self.assertEqual(sn_event.name, MockSN.name)
        self.assertEqual(sn_event.sn_id, '1')

    def test_05_event_finished(self):
        now = tz_now().replace(microsecond=0) - datetime.timedelta(minutes=20)
        end = now + datetime.timedelta(minutes=10)
        event = self._create_event(now, end)

        cron_social_network()
        self.assertEqual(SnEvent.objects.count(), 0)

    def _create_eventlog(self, now, end):
        eventlog = EventLog()
        eventlog.user_id = 1
        eventlog.event = self._create_event(now, end)
        eventlog.msg = 'My Title'
        eventlog.save()
        SnEventLog.objects.all().delete()
        return eventlog

    def test_06_eventlog_default(self):
        now = tz_now().replace(microsecond=0) - datetime.timedelta(minutes=10)
        end = now + datetime.timedelta(minutes=20)
        eventlog = self._create_eventlog(now, end)

        cron_social_network()
        self.assertEqual(SnEventLog.objects.count(), 1)
        sn_eventlog = SnEventLog.objects.get(id=1)
        self.assertEqual(sn_eventlog.eventlog, eventlog)
        self.assertEqual(sn_eventlog.name, MockSN.name)
        self.assertEqual(sn_eventlog.sn_id, '1')

    def test_07_eventlog_future(self):
        now = tz_now().replace(microsecond=0) - datetime.timedelta(minutes=10)
        end = now + datetime.timedelta(minutes=20)
        eventlog = self._create_eventlog(now, end)

        eventlog.date = end
        eventlog.save()
        SnEventLog.objects.all().delete()

        cron_social_network()
        self.assertEqual(SnEventLog.objects.count(), 0)

    def test_08_eventlog_finished(self):
        now = tz_now().replace(microsecond=0) - datetime.timedelta(minutes=20)
        end = now + datetime.timedelta(minutes=10)
        eventlog = self._create_eventlog(now, end)

        cron_social_network()
        self.assertEqual(SnEventLog.objects.count(), 0)
