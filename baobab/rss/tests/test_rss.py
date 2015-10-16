# -*- coding: utf8 --*-
import datetime

from django.db import models
from django.utils.timezone import now as tz_now

from baobab.utils.test import TestCase
from baobab.backoffice.models import Event, EventLog
from baobab.rss.feed import RssStatusFeed


class TestRss(TestCase):

    """ Test RSS Feed """

    fixtures = ['db_user', 'db_backoffice']

    def setUp(self):
        super(TestRss, self).setUp()
        self.rss = RssStatusFeed()

    def test_01_rss_order(self):
        """
        Test if the RSS feed is generated with the good order (pubdate by desc)
        """
        def getKey(last_update):
            return last_update
        event = Event()
        order_expected = sorted(
            [event.last_update for event in Event.objects.all()[:50]], key=getKey, reverse=True)
        items_order = [event.last_update for event in self.rss.items()]
        self.assertListEqual(items_order, order_expected)
        event.date_start = tz_now() + datetime.timedelta(minutes=10)
        event.duration = 120
        event.category = event.MAINTENANCE
        event.summary = ''
        event.save()
        order_expected = sorted(
            [event.last_update for event in Event.objects.all()[:50]], key=getKey, reverse=True)
        items_order = [event.last_update for event in self.rss.items()]
        self.assertListEqual(items_order, order_expected)
        eventlog = EventLog(
            event=event,
            comment='',
            user_id=1)
        eventlog.save()
        order_expected = sorted(
            [event.last_update for event in Event.objects.all()[:50]], key=getKey, reverse=True)
        items_order = [event.last_update for event in self.rss.items()]
        self.assertListEqual(items_order, order_expected)

    def test_02_event_planed_but_not_started(self):
        """
        Test if the event have not tag [] at the beginning of the title
        """
        event = Event()
        event.date_start = tz_now() + datetime.timedelta(days=3)
        event.duration = 120
        event.title = 'My Title'
        event.summary = ''
        event.category = 1
        event.save()
        event = Event.objects.all()[0]
        title = self.rss.item_title(event)
        self.assertEqual(title, 'My Title')

    def test_03_title_event_maintenance_is_started(self):
        """
        Test if the event have been started and if the title is set correctly
        with the tag [STARTED]
        """
        event = Event()
        event.date_start = tz_now() - datetime.timedelta(minutes=10)
        event.duration = 120
        event.title = 'My Title'
        event.summary = ''
        event.category = event.MAINTENANCE
        event.save()
        event = Event.objects.all()[0]
        title = self.rss.item_title(event)
        self.assertEqual(title, '[STARTED] My Title')
        event.date_end = tz_now() + datetime.timedelta(minutes=20)
        event.save()
        title = self.rss.item_title(event)
        self.assertEqual(title, '[STARTED] My Title')

    def test_04_title_event_incident(self):
        """ Test if the event have no tag [STARTED] if it's an incident """
        event = Event()
        event.date_start = tz_now() - datetime.timedelta(minutes=10)
        event.duration = 120
        event.title = 'My Title'
        event.summary = ''
        event.category = event.INCIDENT
        event.save()
        event = Event.objects.all()[0]
        title = self.rss.item_title(event)
        self.assertEqual(title, 'My Title')

    def test_05_event_have_been_update(self):
        """
        Test if the event have been update and if the title is set correctly
        with the tag [UPDATE]
        """
        event = Event()
        event.date_start = tz_now()
        event.duration = 120
        event.title = 'My Title'
        event.summary = ''
        event.category = event.INCIDENT
        event.save()
        event = Event.objects.all()[0]
        eventlog = EventLog(
            event=event,
            comment='Comment',
            user_id=1)
        eventlog.save()
        title = self.rss.item_title(event)
        self.assertEqual(
            title, '[UPDATE %d] My Title' % event.eventlogs.count())

    def test_06_event_is_finished(self):
        """
        Test if the event is finished and if the title is set correctly
        with the tag [FINISHED]
        """
        event = Event()
        event.date_start = tz_now() - datetime.timedelta(minutes=20)
        event.date_end = tz_now() - datetime.timedelta(minutes=10)
        event.title = 'My Title'
        event.summary = ''
        event.category = event.MAINTENANCE
        event.save()
        event = Event.objects.all()[0]
        title = self.rss.item_title(event)
        self.assertEqual(title, '[FINISHED] My Title')

    def test_07_item_link_without_eventlogs(self):
        """
        Test if the item link is formated correctly
        """
        event = Event()
        event.date_start = tz_now()
        event.duration = 120
        event.title = 'My Title'
        event.summary = ''
        event.category = event.INCIDENT
        event.save()
        event = Event.objects.all()[0]
        link = self.rss.item_link(event)
        self.assertEqual(link, '/timeline/events/%d' % event.id)

    def test_08_item_link_with_eventlogs(self):
        """
        Due to cache client, the link should be updated when a new eventlogs
        is added on an event
        """
        event = Event()
        event.date_start = tz_now()
        event.duration = 120
        event.title = 'My title'
        event.summary = ''
        event.category = event.INCIDENT
        event.save()
        eventlog = EventLog(
            event=event,
            comment='Comment',
            user_id=1)
        eventlog.save()
        link = self.rss.item_link(event)
        self.assertEqual(link, '/timeline/events/%d?evnt_id=%d' %
                         (event.id, event.eventlogs.all()[0].id))

    def test_10_item_link_without_eventlogs_but_end_date(self):
        """
        Due to cache client, the link should be updated when the date end is
        set event if there is no event log
        """
        event = Event()
        event.date_start = tz_now() - datetime.timedelta(minutes=20)
        event.date_end = event.date_start + datetime.timedelta(minutes=15)
        event.title = 'My title'
        event.summary = ''
        event.category = event.INCIDENT
        event.save()
        link = self.rss.item_link(event)
        self.assertEqual(link, '/timeline/events/%d?evnt_id=1' % event.id)

    def test_11_rss_title(self):
        """ Test the RSS feed title """
        title = RssStatusFeed.title
        self.assertEqual(title, 'Gandi.net Status RSS Feed')

    def test_12_rss_link_urn(self):
        """ Test if the link is good """
        link = RssStatusFeed.link
        self.assertEqual(link, '/rss/')

    def test_13_rss_description(self):
        """ Test if the Rss description is good """
        description = RssStatusFeed.description
        self.assertEqual(
            description, 'Get information about Gandi platform status')
