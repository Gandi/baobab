# -*- coding: utf-8 -*-
from __future__ import absolute_import

from mock import patch, PropertyMock

from django.conf import settings

from baobab.utils.test import TestCase
from baobab.utils.mock import MockSN, mock_get_field_by_name
from baobab.socialnetwork import SocialNetworks
from baobab.socialnetwork.models import (Event as SnEvent,
                                         EventLog as SnEventLog)
from baobab.backoffice.models import (Event as BoEvent,
                                      EventLog as BoEventLog)


class TestSocialNetwork(TestCase):
    fixtures = ['db_user', 'db_backoffice', ]

    @patch('baobab.utils.mock.MockSN.name',
           new_callable=PropertyMock, return_value=None)
    def test_01_no_name(self, mock_sn):
        sn = SocialNetworks()

        self.assertEqual(self.log._info, [])
        self.assertEqual(len(self.log._error), 1)
        msg = "Couldn't init %s (%s has no name)" % (MockSN, MockSN)
        self.assertEqual(self.log._error[0], msg)

    @patch.object(MockSN, '__init__',
                  side_effect=RuntimeError('MockSN not configured'))
    def test_02_error_on_init(self, mock_sn):
        sn = SocialNetworks()
        self.assertEqual(self.log._info, [])
        self.assertEqual(len(self.log._error), 1)
        msg = "Couldn't init %s (MockSN not configured)" % (MockSN, )
        self.assertEqual(self.log._error[0], msg)

    def test_03_get_url_event(self):
        sn = SocialNetworks()
        url_event = settings.URL_EVENT
        self.assertEqual(sn._get_url_event(42), '%s%d' % (url_event, 42))
        del settings.URL_EVENT
        self.assertEqual(sn._get_url_event(42), '')
        settings.URL_EVENT = url_event

    def test_04_mark_as_publish(self):
        sn = SocialNetworks()
        sn_mock = sn._social_networks[0]

        event = BoEvent.objects.get(id=1)
        filters = {
            'event': event,
            'name': 'MockSN',
        }
        self.assertFalse(SnEvent.objects.filter(**filters).exists())
        sn._mark_as_publish(event, sn_mock.name, 42)
        self.assertTrue(SnEvent.objects.filter(**filters).exists())
        sn_id = SnEvent.objects.filter(**filters).values_list(
            'sn_id', flat=True)[0]
        self.assertEqual(sn_id, '42')

        eventlog = BoEventLog.objects.get(id=1)
        filters = {
            'eventlog': eventlog,
            'name': sn_mock.name,
        }
        self.assertFalse(SnEventLog.objects.filter(**filters).exists())
        sn._mark_as_publish(eventlog, sn_mock.name, 42)
        self.assertTrue(SnEventLog.objects.filter(**filters).exists())
        sn_id = SnEventLog.objects.filter(**filters).values_list(
            'sn_id', flat=True)[0]
        self.assertEqual(sn_id, '42')

    def test_05_is_publish(self):
        sn = SocialNetworks()
        sn_mock = sn._social_networks[0]

        event = BoEvent.objects.get(id=1)
        self.assertFalse(sn._is_publish(event, sn_mock.name))
        SnEvent.objects.create(event=event, name=sn_mock.name, sn_id=42)
        self.assertTrue(sn._is_publish(event, sn_mock.name))

        eventlog = BoEventLog.objects.get(id=1)
        self.assertFalse(sn._is_publish(eventlog, sn_mock.name))
        SnEventLog.objects.create(eventlog=eventlog,
                                       name=sn_mock.name,
                                       sn_id=42)
        self.assertTrue(sn._is_publish(eventlog, sn_mock.name))

    def test_06_empty_msg(self):
        sn = SocialNetworks()
        sn_mock = sn._social_networks[0]

        event = BoEvent.objects.get(id=1)
        self.assertEqual(event.msg, None)
        sn.publish(event)
        self.assertEqual(len(self.log._info), 0)
        self.assertEqual(len(self.log._error), 0)
        self.assertEqual(len(sn_mock._msg), 0)

        eventlog = BoEventLog.objects.get(id=1)
        self.assertEqual(eventlog.msg, None)
        sn.publish(eventlog)
        self.assertEqual(len(self.log._info), 0)
        self.assertEqual(len(self.log._error), 0)
        self.assertEqual(len(sn_mock._msg), 0)

    def test_07_published_msg(self):
        sn = SocialNetworks()
        sn_mock = sn._social_networks[0]

        event = BoEvent.objects.get(id=1)
        # XXX don't save the obj we don't want to test the post_save trigger
        event.msg = 'not empyt event'
        SnEvent.objects.create(event=event, name=sn_mock.name, sn_id=42)
        sn.publish(event)
        self.assertEqual(len(self.log._info), 0)
        self.assertEqual(len(self.log._error), 0)
        self.assertEqual(len(sn_mock._msg), 0)

        eventlog = BoEventLog.objects.get(id=1)
        # XXX don't save the obj we don't want to test the post_save trigger
        eventlog.msg = 'not empyt eventlog'
        SnEventLog.objects.create(eventlog=eventlog,
                                       name=sn_mock.name, sn_id=42)
        sn.publish(eventlog)
        self.assertEqual(len(self.log._info), 0)
        self.assertEqual(len(self.log._error), 0)
        self.assertEqual(len(sn_mock._msg), 0)

    @patch.object(MockSN, 'publish',
                  side_effect=RuntimeError('not connected'))
    def test_08_publish_error(self, mock_sn):
        sn = SocialNetworks()
        sn_mock = sn._social_networks[0]

        event = BoEvent.objects.get(id=1)
        # XXX don't save the obj we don't want to test the post_save trigger
        event.msg = 'not empyt event'
        sn.publish(event)
        self.assertEqual(len(self.log._info), 0)
        self.assertEqual(len(self.log._error), 1)
        msg = "Can't publish msg: %s, event_id: %d for sn: %s (%s)" % (
            event.msg, event.id, sn_mock.name, 'not connected')
        self.assertEqual(self.log._error[0], msg)
        self.assertEqual(len(sn_mock._msg), 0)

        eventlog = BoEventLog.objects.get(id=1)
        # XXX don't save the obj we don't want to test the post_save trigger
        eventlog.msg = 'not empyt eventlog'
        sn.publish(eventlog)
        self.assertEqual(len(self.log._info), 0)
        self.assertEqual(len(self.log._error), 2)
        msg = "Can't publish msg: %s, event_id: %d for sn: %s (%s)" % (
            eventlog.msg, eventlog.event.id,
            sn_mock.name, 'not connected')
        self.assertEqual(self.log._error[1], msg)
        self.assertEqual(len(sn_mock._msg), 0)

    def test_09_publish(self):
        sn = SocialNetworks()
        sn_mock = sn._social_networks[0]

        event = BoEvent.objects.get(id=1)
        # XXX don't save the obj we don't want to test the post_save trigger
        event.msg = 'not empyt event'
        filters = {
            'event': event,
            'name': 'MockSN',
        }
        self.assertFalse(SnEvent.objects.filter(**filters).exists())
        sn.publish(event)
        self.assertTrue(SnEvent.objects.filter(**filters).exists())
        self.assertEqual(len(self.log._info), 1)
        url = '%s%d' % (settings.URL_EVENT, event.id)
        msg = 'publish sn: %s msg: %s, url: %s' % (
            sn_mock.name, event.msg, url)
        self.assertEqual(self.log._info[0], msg)
        self.assertEqual(len(self.log._error), 0)
        self.assertEqual(len(sn_mock._msg), 1)
        self.assertEqual(sn_mock._msg[0], (event.msg, url))

        eventlog = BoEventLog.objects.get(id=1)
        # XXX don't save the obj we don't want to test the post_save trigger
        eventlog.msg = 'not empyt eventlog'
        filters = {
            'eventlog': eventlog,
            'name': 'MockSN',
        }
        self.assertFalse(SnEventLog.objects.filter(**filters).exists())
        sn.publish(eventlog)
        self.assertTrue(SnEventLog.objects.filter(**filters).exists())
        self.assertEqual(len(self.log._info), 2)
        url = '%s%d' % (settings.URL_EVENT, eventlog.event.id)
        msg = 'publish sn: %s msg: %s, url: %s' % (
            sn_mock.name, eventlog.msg, url)
        self.assertEqual(self.log._info[1], msg)
        self.assertEqual(len(self.log._error), 0)
        self.assertEqual(len(sn_mock._msg), 2)
        self.assertEqual(sn_mock._msg[1], (eventlog.msg, url))

    @patch('baobab.socialnetwork.base.BackOfficeEvent._meta.get_field_by_name',
           return_value=mock_get_field_by_name())
    def test_10_get_max_char_ko(self, field_msg):
        sn = SocialNetworks()
        msg = 'BackOfficeEvent.msg and BackOfficeEventLog.msg HAS TO have ' \
              'the same max length'
        self.assertRaisesRegexp(RuntimeError, msg, sn.get_max_char)

    def test_11_get_max_char_ok(self):
        sn = SocialNetworks()
        self.assertEqual(sn.get_max_char(), 42)
