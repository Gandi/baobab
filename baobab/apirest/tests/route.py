# -*- coding: utf-8 -*-
"""
check that only the expected route are really defined
"""

from django.core.urlresolvers import RegexURLPattern, RegexURLResolver

from tastypie.test import ResourceTestCase

from baobab.apirest.urls import ApiUrls
from baobab.apirest.tests.schema import TestSchema


class TestRoute(ResourceTestCase):

    nb_route = 3  # status, services, events

    # XXX default route are:
    #     list_view
    #     list_view/set/{id}
    #     schema
    #     detail_view/{id}
    nb_default_route_by_ressource = 4

    # XXX default to 4, +2 to correctly handle the route events/{id}
    nb_route_for_event = 6

    def test_01_nb_of_route(self):
        urls = ApiUrls.get_urls()
        # check the nb of defined ressources should be the same as the
        # number of route + 1 done by tastypie
        self.assertEqual(len(urls), self.nb_route + 1)
        self.assertTrue(isinstance(urls.pop(0), RegexURLPattern))

        event_url = urls.pop(0)
        self.assertTrue(isinstance(event_url, RegexURLResolver))
        # XXX depend on the version of tastypie: only use one or both method:
        #     prepend_urls/override_urls
        self.assertIn(len(event_url.url_patterns),
                      [self.nb_route_for_event, self.nb_route_for_event + 2])

        for url in urls:
            self.assertTrue(isinstance(url, RegexURLResolver))
            self.assertEqual(len(url.url_patterns),
                             self.nb_default_route_by_ressource)

    def test_02_nb_route_schema(self):
        self.assertEqual(len(TestSchema.routes), self.nb_route)
