# -*- coding: utf-8 -*-
import datetime

from django.utils.timezone import now as tz_now

from baobab.utils.test import TestCase
from baobab.utils.mock import MockSN

from baobab.backoffice.models import Event, EventLog
from baobab.socialnetwork.models import EventLog as SnEventLog


class TestEventLogTrigger(TestCase):
    fixtures = ['db_user', 'db_backoffice']

    def _create_eventlog(self, now, end, category):
        event = Event()
        event.date_start = now
        event.date_end = end
        event.title = 'My Title'
        event.summary = ''
        event.category = category
        event.msg = None  # to not trigger the event on_event
        event.save()
        eventlog = EventLog()
        eventlog.user_id = 1
        eventlog.event = event
        eventlog.comment = ''
        eventlog.msg = 'a eventlog msg'
        eventlog.save()
        return eventlog

    def test_01_eventlog_incident_now(self):
        self.assertEqual(SnEventLog.objects.count(), 0)

        now = tz_now().replace(microsecond=0)
        end = now + datetime.timedelta(minutes=10)
        eventlog = self._create_eventlog(now, end, Event.INCIDENT)

        self.assertEqual(SnEventLog.objects.count(), 1)
        sn_eventlog = SnEventLog.objects.get(id=1)
        self.assertEqual(sn_eventlog.eventlog, eventlog)
        self.assertEqual(sn_eventlog.name, MockSN.name)
        self.assertEqual(sn_eventlog.sn_id, '1')

    def test_02_eventlog_incident_past(self):
        self.assertEqual(SnEventLog.objects.count(), 0)

        now = tz_now().replace(microsecond=0) - datetime.timedelta(minutes=20)
        end = now - datetime.timedelta(minutes=10)
        eventlog = self._create_eventlog(now, end, Event.INCIDENT)

        self.assertEqual(SnEventLog.objects.count(), 1)
        sn_eventlog = SnEventLog.objects.get(id=1)
        self.assertEqual(sn_eventlog.eventlog, eventlog)
        self.assertEqual(sn_eventlog.name, MockSN.name)
        self.assertEqual(sn_eventlog.sn_id, '1')

    def test_03_eventlog_incident_futre(self):
        self.assertEqual(SnEventLog.objects.count(), 0)

        now = tz_now().replace(microsecond=0) + datetime.timedelta(minutes=10)
        end = now + datetime.timedelta(minutes=10)
        eventlog = self._create_eventlog(now, end, Event.INCIDENT)

        self.assertEqual(SnEventLog.objects.count(), 1)
        sn_eventlog = SnEventLog.objects.get(id=1)
        self.assertEqual(sn_eventlog.eventlog, eventlog)
        self.assertEqual(sn_eventlog.name, MockSN.name)
        self.assertEqual(sn_eventlog.sn_id, '1')

    def test_04_eventlog_maintenace_now(self):
        self.assertEqual(SnEventLog.objects.count(), 0)

        now = tz_now().replace(microsecond=0)
        end = now + datetime.timedelta(minutes=10)
        eventlog = self._create_eventlog(now, end, Event.MAINTENANCE)

        self.assertEqual(SnEventLog.objects.count(), 1)
        sn_eventlog = SnEventLog.objects.get(id=1)
        self.assertEqual(sn_eventlog.eventlog, eventlog)
        self.assertEqual(sn_eventlog.name, MockSN.name)
        self.assertEqual(sn_eventlog.sn_id, '1')

    def test_05_eventlog_maintenace_past(self):
        self.assertEqual(SnEventLog.objects.count(), 0)

        now = tz_now().replace(microsecond=0) - datetime.timedelta(minutes=20)
        end = now - datetime.timedelta(minutes=10)
        eventlog = self._create_eventlog(now, end, Event.MAINTENANCE)

        self.assertEqual(SnEventLog.objects.count(), 1)
        sn_eventlog = SnEventLog.objects.get(id=1)
        self.assertEqual(sn_eventlog.eventlog, eventlog)
        self.assertEqual(sn_eventlog.name, MockSN.name)
        self.assertEqual(sn_eventlog.sn_id, '1')

    def test_06_eventlog_maintenace_futre(self):
        self.assertEqual(SnEventLog.objects.count(), 0)

        now = tz_now().replace(microsecond=0) + datetime.timedelta(minutes=10)
        end = now + datetime.timedelta(minutes=10)
        eventlog = self._create_eventlog(now, end, Event.MAINTENANCE)

        self.assertEqual(SnEventLog.objects.count(), 0)
