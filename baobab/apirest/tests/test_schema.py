# -*- coding: utf-8 -*-
"""
check that only the expected route are really defined
"""

import json

from django.core.urlresolvers import RegexURLPattern, RegexURLResolver

from baobab.utils.test import ResourceTestCase
from baobab.apirest.urls import ApiUrls


class TestSchema(ResourceTestCase):

    routes = [
        'events',
        'services',
        'status',
    ]

    def test_route_json(self):
        resp = self.api_client.get('/api')
        self.assertValidJSONResponse(resp)
        for route in self.routes:
            resp = self.api_client.get('/api/%s/schema' % route)
            self.assertValidJSONResponse(resp)

    def test_route_html(self):
        resp = self.api_client.get('/api', format='html')
        self.assertHttpOK(resp)
        for route in self.routes:
            resp = self.api_client.get('/api/%s/schema' % route, format='html')
            self.assertHttpOK(resp)
