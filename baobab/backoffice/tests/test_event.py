# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.utils.timezone import now as tz_now

from baobab.utils.test import TestCase
from baobab.backoffice.models import Event


class TestEvent(TestCase):
    fixtures = ['db_user', 'db_backoffice']

    def test_01_create_with_date_end(self):
        event = Event()
        now = tz_now().replace(microsecond=0)
        end = now + datetime.timedelta(minutes=10)
        event.date_start = now
        event.date_end = end
        event.title = 'My Title'
        event.summary = ''
        event.category = 1
        event.save()
        event = Event.objects.get(title='My Title')
        self.assertEqual(event.date_start, now)
        self.assertEqual(event.date_end, None)
        self.assertEqual(event.duration, 10)
        self.assertEqual(event.estimate_date_end, end)

    def test_02_create_without_end(self):
        event = Event()
        now = tz_now().replace(microsecond=0)
        end = now + datetime.timedelta(minutes=10)
        event.date_start = now
        event.duration = 10
        event.title = 'My Title'
        event.summary = ''
        event.category = 1
        event.save()
        event = Event.objects.get(title='My Title')
        self.assertEqual(event.date_start, now)
        self.assertEqual(event.date_end, None)
        self.assertEqual(event.duration, 10)
        self.assertEqual(event.estimate_date_end, end)

    def test_03_set_date_end(self):
        event = Event()
        now = tz_now().replace(microsecond=0)
        end = now + datetime.timedelta(minutes=20)
        event.date_start = now
        event.duration = 10
        event.title = 'My Title'
        event.summary = ''
        event.category = 1
        event.save()
        event.date_end = end
        event.save()
        event = Event.objects.get(title='My Title')
        self.assertEqual(event.date_start, now)
        self.assertEqual(event.date_end, end)
        self.assertEqual(event.duration, 20)
        self.assertEqual(event.estimate_date_end,
                         event.date_start + datetime.timedelta(minutes=10))

    def test_04_order(self):
        # XXX to be able to use the default manager
        #     without the override of the sort
        mm = models.Manager()
        mm.contribute_to_class(Event, 'default_objects')
        default_order = [event.id for event in Event.default_objects.all()]
        self.assertEqual(default_order, [1, 2, 3, 4, 5, 6])
        override_order = [event.id for event in Event.objects.all()]
        self.assertEqual(override_order, [2, 3, 1, 4, 5, 6])
        choose_order = [event.id for event in
                        Event.objects.order_by('title')]
        self.assertEqual(choose_order, [3, 2, 1, 4, 5, 6])

    def test_05_postpone_no_date_end(self):
        event = Event()
        now = tz_now().replace(microsecond=0)
        end = now + datetime.timedelta(minutes=10)
        event.date_start = now
        event.duration = 10
        event.title = 'My Title'
        event.summary = ''
        event.category = 1
        event.save()

        event = Event.objects.get(title='My Title')
        self.assertEqual(event.date_end, None)
        self.assertEqual(event.estimate_date_end, end)
        event.date_start = now + datetime.timedelta(minutes=10)
        event.save()

        event = Event.objects.get(title='My Title')
        self.assertEqual(event.date_end, None)
        self.assertEqual(event.estimate_date_end,
                         end + datetime.timedelta(minutes=10))

    def test_06_postpone_with_date_end(self):
        event = Event()
        now = tz_now().replace(microsecond=0)
        end = now + datetime.timedelta(minutes=10)
        event.date_start = now
        event.duration = 10
        event.title = 'My Title'
        event.summary = ''
        event.category = 1
        event.save()
        event.date_end = end
        event.save()

        event = Event.objects.get(title='My Title')
        self.assertEqual(event.date_start, now)
        self.assertEqual(event.date_end, end)
        self.assertEqual(event.estimate_date_end, end)
        self.assertEqual(event.duration, 10)
        event.date_start = end
        event.date_end = event.date_start + datetime.timedelta(minutes=12)
        event.save()

        event = Event.objects.get(title='My Title')
        self.assertEqual(event.date_start, end)
        self.assertEqual(event.date_end, end + datetime.timedelta(minutes=12))
        self.assertEqual(event.estimate_date_end, event.date_end)
        self.assertEqual(event.duration, 12)
