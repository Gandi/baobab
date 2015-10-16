# -*- coding: utf-8 -*-
from __future__ import absolute_import

from mock import patch

from django.test import TestCase as DjangoTestCase
from tastypie.test import ResourceTestCase as TastypieResourceTestCase

from baobab.utils.mock import MockSN, MockLOG


class TestCase(DjangoTestCase):

    def setUp(self, *args, **kwargs):
        super(TestCase, self).setUp(*args, **kwargs)
        self._mock = []

        cls_path = 'baobab.socialnetwork.base.LOG'
        self._mock.append(patch(cls_path, new_callable=MockLOG))
        self.log = self._mock[0].start()

        cls_path = 'baobab.socialnetwork.base.SocialNetworkBase.__subclasses__'
        self._mock.append(patch(cls_path, return_value=[MockSN, ]))
        self._mock[1].start()

    def tearDown(self, *args, **kwargs):
        super(TestCase, self).tearDown(*args, **kwargs)
        for mock in self._mock:
            mock.stop()


class ResourceTestCase(TastypieResourceTestCase):

    def setUp(self, *args, **kwargs):
        super(ResourceTestCase, self).setUp(*args, **kwargs)
        self._mock = []

        cls_path = 'baobab.socialnetwork.base.LOG'
        self._mock.append(patch(cls_path, new_callable=MockLOG))
        self.log = self._mock[0].start()

        cls_path = 'baobab.socialnetwork.base.SocialNetworkBase.__subclasses__'
        self._mock.append(patch(cls_path, return_value=[MockSN, ]))
        self._mock[1].start()

    def tearDown(self, *args, **kwargs):
        super(ResourceTestCase, self).tearDown(*args, **kwargs)
        for mock in self._mock:
            mock.stop()
