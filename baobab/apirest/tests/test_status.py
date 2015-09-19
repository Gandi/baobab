# -*- coding: utf-8 -*-

from datetime import timedelta

from django.utils.timezone import now

from tastypie.http import HttpMethodNotAllowed

from baobab.utils.test import ResourceTestCase
from baobab.backoffice.models import Event as BOEvent


class TestStatus(ResourceTestCase):
    fixtures = ['db_user', 'db_backoffice']

    url = '/api/status'

    def _create_event(self, duration, services, category):
        event = BOEvent()
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

    def test_01_get_list(self):
        resp = self.api_client.get(self.url)
        self.assertValidJSONResponse(resp)

    def test_02_get_detail(self):
        resp = self.api_client.get('%s/1' % self.url)
        self.assertEqual(type(resp), HttpMethodNotAllowed)

    def test_03_OK(self):
        resp = self.api_client.get(self.url)
        data = self.deserialize(resp)
        self.assertEqual(data, {'status': u'SUNNY'})

    def test_04_CLOUDY(self):
        event = self._create_event(10, [1, 2], BOEvent.MAINTENANCE)
        resp = self.api_client.get(self.url)
        data = self.deserialize(resp)
        self.assertEqual(data, {'status': u'CLOUDY'})

    def test_05_STORMY(self):
        event = self._create_event(10, [1, 2], BOEvent.INCIDENT)
        resp = self.api_client.get(self.url)
        data = self.deserialize(resp)
        self.assertEqual(data, {'status': u'STORMY'})

    def test_06_STORMY_CLOUDY(self):
        cloudy = self._create_event(10, [1, 2], BOEvent.MAINTENANCE)
        stormy = self._create_event(10, [3, 4], BOEvent.INCIDENT)
        resp = self.api_client.get(self.url)
        data = self.deserialize(resp)
        self.assertEqual(data, {'status': u'STORMY'})
        stormy.end()
        resp = self.api_client.get(self.url)
        data = self.deserialize(resp)
        self.assertEqual(data, {'status': u'CLOUDY'})

    def test_07_FOGGY(self):
        foggy = self._create_event(10, [], BOEvent.INCIDENT)
        resp = self.api_client.get(self.url)
        data = self.deserialize(resp)
        self.assertEqual(data, {'status': u'FOGGY'})

    def test_08_STORMY_FOGGY(self):
        foggy = self._create_event(10, [], BOEvent.INCIDENT)
        stormy = self._create_event(10, [3, 4], BOEvent.INCIDENT)
        resp = self.api_client.get(self.url)
        data = self.deserialize(resp)
        self.assertEqual(data, {'status': u'STORMY'})
        stormy.end()
        resp = self.api_client.get(self.url)
        data = self.deserialize(resp)
        self.assertEqual(data, {'status': u'FOGGY'})

    def test_09_NOT_FOGGY(self):
        couldy = self._create_event(10, [], BOEvent.MAINTENANCE)
        resp = self.api_client.get(self.url)
        data = self.deserialize(resp)
        self.assertEqual(data, {'status': u'CLOUDY'})

    def test_10_FOGGY_CLOUDY(self):
        foggy = self._create_event(10, [], BOEvent.INCIDENT)
        could = self._create_event(10, [], BOEvent.MAINTENANCE)
        resp = self.api_client.get(self.url)
        data = self.deserialize(resp)
        self.assertEqual(data, {'status': u'FOGGY'})
        foggy.end()
        resp = self.api_client.get(self.url)
        data = self.deserialize(resp)
        self.assertEqual(data, {'status': u'CLOUDY'})
