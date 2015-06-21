# -*- coding: utf-8 -*-
import datetime

from django.utils.timezone import now

from tastypie.test import ResourceTestCase

from baobab.backoffice.models import Service as BOService


class TestServices(ResourceTestCase):
    fixtures = ['db_user', 'db_backoffice']

    url = '/api/services'

    def test_01_get_list(self):
        resp = self.api_client.get(self.url)
        self.assertValidJSONResponse(resp)

    def test_02_number_of_elem(self):
        resp = self.api_client.get(self.url)
        data = self.deserialize(resp)
        self.assertEqual(len(data), len(BOService.SERVICE_CHOICES))

    def test_03_key(self):
        resp = self.api_client.get(self.url)
        datas = self.deserialize(resp)
        for data in datas:
            self.assertKeys(data, ['name', 'description', 'status'])

    def test_04_name(self):
        resp = self.api_client.get(self.url)
        datas = self.deserialize(resp)
        names = [val for _, val in BOService.SERVICE_CHOICES]
        for data in datas:
            self.assertTrue(data['name'] in names)
