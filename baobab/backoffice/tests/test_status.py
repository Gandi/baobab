# -*- coding: utf-8 -*-
import datetime

from django.utils.timezone import now

from baobab.utils.test import TestCase
from baobab.backoffice.models import Event, Service


class TestStatus(TestCase):
    fixtures = ['db_user', 'db_backoffice']

    def _create_event(self, duration, services, category):
        event = Event()
        event.date_start = now()
        event.duration = duration
        event.title = 'My Title: %d' % duration
        event.summary = ''
        event.category = category
        event.save()
        event.services.add(*services)

        def _end_event(event=event):
            event.date_end = now()
            event.save()

        event.end = _end_event
        return event

    def _check_status(self, cloudy=[], stormy=[]):
        nb_cloudy = 0
        nb_stormy = 0
        for service in Service.objects.all():
            if service.id in cloudy:
                self.assertEqual(service.status, Service.CLOUDY)
                self.assertEqual(service.get_status_display(), 'CLOUDY')
                nb_cloudy += 1
            elif service.id in stormy:
                self.assertEqual(service.status, Service.STORMY)
                self.assertEqual(service.get_status_display(), 'STORMY')
                nb_stormy += 1
            else:
                self.assertEqual(service.status, Service.SUNNY)
                self.assertEqual(service.get_status_display(), 'SUNNY')
        self.assertEqual(nb_cloudy, len(cloudy))
        self.assertEqual(nb_stormy, len(stormy))

    def test_01_SUNNY(self):
        for service in Service.objects.all():
            self.assertEqual(service.status, Service.SUNNY)
            self.assertEqual(service.get_status_display(), 'SUNNY')

    def test_02_CLOUDY_1_service(self):
        cloudy = [1, ]
        event = self._create_event(10, cloudy, Event.MAINTENANCE)
        self._check_status(cloudy=cloudy)
        event.end()
        self._check_status([])

    def test_03_CLOUDY_2_service(self):
        cloudy = [1, 3]
        event = self._create_event(10, cloudy, Event.MAINTENANCE)
        self._check_status(cloudy=cloudy)
        event.end()
        self._check_status([])

    def test_04_STORMY_1_service(self):
        stormy = [1, ]
        event = self._create_event(10, stormy, Event.INCIDENT)
        self._check_status(stormy=stormy)
        event.end()
        self._check_status([])

    def test_05_STORMY_2_service(self):
        stormy = [1, 3]
        event = self._create_event(10, stormy, Event.INCIDENT)
        self._check_status(stormy=stormy)
        event.end()
        self._check_status([])

    def test_06_KO_2_event(self):
        cloudy = [1]
        stormy = [3]
        cloudy_event = self._create_event(60, cloudy, Event.MAINTENANCE)
        stormy_event = self._create_event(20, stormy, Event.INCIDENT)
        self._check_status(cloudy=cloudy, stormy=stormy)
        stormy_event.end()
        self._check_status(cloudy=cloudy)
        cloudy_event.end()
        self._check_status()

    def test_07_KO_2_event_same_service(self):
        cloudy = [1]
        stormy = [1]
        cloudy_event = self._create_event(60, cloudy, Event.MAINTENANCE)
        stormy_event = self._create_event(20, stormy, Event.INCIDENT)
        self._check_status(stormy=stormy)  # stormy override stormy
        stormy_event.end()
        self._check_status(cloudy=cloudy)
        cloudy_event.end()
        self._check_status()

    def test_08_KO_2_event_2_service(self):
        cloudy = [1, 3, 4, 5]
        event1 = self._create_event(60, cloudy[0:2], Event.MAINTENANCE)
        event2 = self._create_event(20, cloudy[2:], Event.MAINTENANCE)
        self._check_status(cloudy)
        event2.end()
        self._check_status(cloudy[0:2])
        event1.end()
        self._check_status([])

    def test_09_estimate_date_end_in_the_past(self):
        cloudy = [1, 3, 4, 5]
        event = self._create_event(20, cloudy, Event.MAINTENANCE)
        event.date_start = now() + datetime.timedelta(minutes=-60)
        event.save()
        self._check_status(cloudy)
        event.end()
        self._check_status([])
