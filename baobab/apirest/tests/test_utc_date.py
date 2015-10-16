# -*- coding: utf-8 -*-

import datetime
import pytz

from django.conf import settings
from django.utils.timezone import is_naive, now

from baobab.utils.test import TestCase
from baobab.apirest.modelresource import MySerializer


class TestUTCDate(TestCase):
    url = '/api/services'

    def test_01_native_date(self):
        date = datetime.datetime(2014, 5, 9, 18, 00)
        tz = pytz.timezone(settings.TIME_ZONE)
        self.assertTrue(is_naive(date))
        api_date = MySerializer().format_datetime(date)
        date = date - tz.utcoffset(date)
        self.assertEqual(api_date, date.strftime('%Y-%m-%dT%H:%M:%S+00:00'))

    def test_02_default_tz(self):
        tz = pytz.timezone(settings.TIME_ZONE)
        date = datetime.datetime(2014, 5, 9, 18, 00, tzinfo=tz)
        self.assertFalse(is_naive(date))
        api_date = MySerializer().format_datetime(date)
        date = date - tz.utcoffset(date)
        #date = date.astimezone(pytz.UTC)
        self.assertEqual(api_date, date.strftime('%Y-%m-%dT%H:%M:%S+00:00'))

    def test_03_utc_tz(self):
        date = datetime.datetime(2014, 5, 9, 18, 00, tzinfo=pytz.UTC)
        self.assertFalse(is_naive(date))
        api_date = MySerializer().format_datetime(date)
        self.assertEqual(api_date, date.strftime('%Y-%m-%dT%H:%M:%S+00:00'))

    def test_04_another_tz(self):
        tz = pytz.timezone('US/Hawaii')
        date = datetime.datetime(2014, 5, 9, 18, 00, tzinfo=tz)
        self.assertFalse(is_naive(date))
        api_date = MySerializer().format_datetime(date)
        date = date - tz.utcoffset(date)
        #date = date.astimezone(pytz.UTC)
        self.assertEqual(api_date, date.strftime('%Y-%m-%dT%H:%M:%S+00:00'))

    def test_05_no_microsecond(self):
        date = now()
        api_date = MySerializer().format_datetime(date)
        self.assertEqual(api_date, date.strftime('%Y-%m-%dT%H:%M:%S+00:00'))
