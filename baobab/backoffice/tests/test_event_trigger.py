# -*- coding: utf-8 -*-
import datetime

from django.utils.timezone import now as tz_now

from baobab.utils.test import TestCase
from baobab.utils.mock import MockSN
from baobab.backoffice.models import Event
from baobab.socialnetwork.models import Event as SnEvent


class TestEventTrigger(TestCase):
    fixtures = ['db_user', 'db_backoffice']

    def _create_event(self, now, end, category):
        event = Event()
        event.date_start = now
        event.date_end = end
        event.title = 'My Title'
        event.summary = ''
        event.category = category
        event.msg = 'a msg to publish'
        event.save()
        return event

    def test_01_event_incident_now(self):
        self.assertEqual(SnEvent.objects.count(), 0)

        now = tz_now().replace(microsecond=0)
        end = now + datetime.timedelta(minutes=10)
        event = self._create_event(now, end, Event.INCIDENT)

        self.assertEqual(SnEvent.objects.count(), 1)
        sn_event = SnEvent.objects.get(id=1)
        self.assertEqual(sn_event.event, event)
        self.assertEqual(sn_event.name, MockSN.name)
        self.assertEqual(sn_event.sn_id, '1')

    def test_02_event_incident_past(self):
        self.assertEqual(SnEvent.objects.count(), 0)

        now = tz_now().replace(microsecond=0) - datetime.timedelta(minutes=20)
        end = now - datetime.timedelta(minutes=10)
        event = self._create_event(now, end, Event.INCIDENT)

        self.assertEqual(SnEvent.objects.count(), 1)
        sn_event = SnEvent.objects.get(id=1)
        self.assertEqual(sn_event.event, event)
        self.assertEqual(sn_event.name, MockSN.name)
        self.assertEqual(sn_event.sn_id, '1')

    def test_03_event_incident_futre(self):
        self.assertEqual(SnEvent.objects.count(), 0)

        now = tz_now().replace(microsecond=0) + datetime.timedelta(minutes=10)
        end = now + datetime.timedelta(minutes=10)
        event = self._create_event(now, end, Event.INCIDENT)

        self.assertEqual(SnEvent.objects.count(), 1)
        sn_event = SnEvent.objects.get(id=1)
        self.assertEqual(sn_event.event, event)
        self.assertEqual(sn_event.name, MockSN.name)
        self.assertEqual(sn_event.sn_id, '1')

    def test_04_event_maintenace_now(self):
        self.assertEqual(SnEvent.objects.count(), 0)

        now = tz_now().replace(microsecond=0)
        end = now + datetime.timedelta(minutes=10)
        event = self._create_event(now, end, Event.MAINTENANCE)

        self.assertEqual(SnEvent.objects.count(), 1)
        sn_event = SnEvent.objects.get(id=1)
        self.assertEqual(sn_event.event, event)
        self.assertEqual(sn_event.name, MockSN.name)
        self.assertEqual(sn_event.sn_id, '1')

    def test_05_event_maintenace_past(self):
        self.assertEqual(SnEvent.objects.count(), 0)

        now = tz_now().replace(microsecond=0) - datetime.timedelta(minutes=20)
        end = now - datetime.timedelta(minutes=10)
        event = self._create_event(now, end, Event.MAINTENANCE)

        self.assertEqual(SnEvent.objects.count(), 1)
        sn_event = SnEvent.objects.get(id=1)
        self.assertEqual(sn_event.event, event)
        self.assertEqual(sn_event.name, MockSN.name)
        self.assertEqual(sn_event.sn_id, '1')

    def test_06_event_maintenace_futre(self):
        self.assertEqual(SnEvent.objects.count(), 0)

        now = tz_now().replace(microsecond=0) + datetime.timedelta(minutes=10)
        end = now + datetime.timedelta(minutes=10)
        event = self._create_event(now, end, Event.MAINTENANCE)

        self.assertEqual(SnEvent.objects.count(), 0)
