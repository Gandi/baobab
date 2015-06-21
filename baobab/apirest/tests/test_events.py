# -*- coding: utf-8 -*-
import datetime

from django.utils.timezone import now

from tastypie.test import ResourceTestCase

from baobab.backoffice.models import (Service as BOService,
                                      EventLog as BOEventLog,
                                      Event as BOEvent)
from baobab.translate.models import EventData, EventLogData, Lang
from baobab.translate.adminfilter import (EventCompleteFilter,
                                          EventLogCompleteFilter)


class TestEvents(ResourceTestCase):
    fixtures = ['db_user', 'db_backoffice', 'db_translate']

    url = '/api/events'
    list_key = ['category', 'date_end', 'date_start', 'last_update',
                'duration', 'estimate_date_end', 'id', 'services',
                'title']
    detail_key = list(list_key)
    detail_key.extend(['logs', 'summary'])
    logs_key = ['comment', 'date', 'id']

    def _create_event(self, duration, services, category):
        event = BOEvent()
        event.date_start = now()
        event.duration = duration
        event.title = 'My Title: %d' % duration
        event.summary = ''
        event.category = category
        event.save()
        event.services.add(*services)
        EventData.objects.create(event=event, lang_id=1,
                                 title=event.title, user_id=1)

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
        self.assertValidJSONResponse(resp)

    def test_03_key_list(self):
        resp = self.api_client.get(self.url)
        data = self.deserialize(resp)
        self.assertKeys(data[0], self.list_key)

    def test_04_key_detail(self):
        resp = self.api_client.get('%s/1' % self.url)
        data = self.deserialize(resp)
        self.assertKeys(data, self.detail_key)
        for log in data['logs']:
            self.assertKeys(log, self.logs_key)

    def test_05_order(self):
        # XXX this is already test in backoffice.test.TestService.test_04_order
        #     since the admin override the order check the output
        #     of the api just to be sure
        resp = self.api_client.get(self.url)
        data = self.deserialize(resp)
        override_order = [event['id'] for event in data]
        self.assertEqual(override_order, [2, 3, 1, 4, 5, 6])


#  test the translate part of the api

    def test_06_events_language(self):
        resp = self.api_client.get(self.url, HTTP_ACCEPT_LANGUAGE='fr')
        self.assertEqual(resp.get('Content-Language'), None)
        BOEvent.objects.exclude(pk=2).delete()
        resp = self.api_client.get(self.url, HTTP_ACCEPT_LANGUAGE='fr')
        self.assertEqual(resp.get('Content-Language'), 'fr')

    def test_07_events_language_translated(self):
        resp_fr = self.api_client.get('%s/2' % self.url,
                                      HTTP_ACCEPT_LANGUAGE='fr')
        self.assertEqual(resp_fr.get('Content-Language'), 'fr')
        resp_en = self.api_client.get('%s/2' % self.url,
                                      HTTP_ACCEPT_LANGUAGE='en')
        self.assertEqual(resp_en.get('Content-Language'), 'en')
        resp_es = self.api_client.get('%s/2' % self.url,
                                      HTTP_ACCEPT_LANGUAGE='es')
        self.assertEqual(resp_en.get('Content-Language'), 'en')

        resp_en = self.deserialize(resp_en)
        resp_es = self.deserialize(resp_es)
        resp_fr = self.deserialize(resp_fr)
        self.assertEqual(resp_es['title'], resp_en['title'])
        self.assertEqual(resp_es['summary'], resp_en['summary'])
        self.assertNotEqual(resp_fr['title'], resp_en['title'])
        self.assertNotEqual(resp_fr['summary'], resp_en['summary'])
        for idx in range(len(resp_en['logs'])):
            self.assertEqual(resp_es['logs'][idx], resp_en['logs'][idx])
            self.assertNotEqual(resp_fr['logs'][idx], resp_en['logs'][idx])

    def _add_missing_datas(self):
        for lang in ['es', 'zh-SG', 'zh-TW']:
            lang = Lang.objects.get(iso=lang)
            event = BOEvent.objects.get(pk=2)
            EventData.objects.create(
                title='a title',
                summary='a summary',
                event=event,
                lang=lang
            )

    def _add_missing_datalogs(self):
        for lang in ['es', 'zh-SG', 'zh-TW']:
            lang = Lang.objects.get(iso=lang)
            for eventlog in BOEventLog.objects.filter(event_id=2):
                EventLogData.objects.create(
                    comment='a msg',
                    eventlog=eventlog,
                    lang=lang
                )

    def _check_filter(self, cls_model, cls_filter, key_filter,
                      nb_false, nb_true):
        filter_ = cls_filter(None, {key_filter: 'true'}, None, None)
        res_false = filter_.queryset(None, cls_model.objects).count()
        self.assertEqual(nb_false, res_false)
        filter_ = cls_filter(None, {key_filter: 'false'}, None, None)
        res_true = filter_.queryset(None, cls_model.objects).count()
        self.assertEqual(nb_true, res_true)

    def test_08_filterlogs(self):
        nb_log = BOEventLog.objects.count()
        self._check_filter(BOEventLog, EventLogCompleteFilter, 'completelog',
                           0, nb_log)
        self._add_missing_datalogs()
        nb_log_ok = BOEventLog.objects.filter(event_id=2).count()
        self._check_filter(BOEventLog, EventLogCompleteFilter, 'completelog',
                           nb_log_ok, nb_log - nb_log_ok)

    def test_09_filterdatas(self):
        nb_data = BOEvent.objects.count()
        self._check_filter(BOEvent, EventCompleteFilter, 'complete', 0, nb_data)
        # missing some log so nothing should change
        self._add_missing_datas()
        self._check_filter(BOEvent, EventCompleteFilter, 'complete', 0, nb_data)
        EventData.objects.filter(
            event_id=2,
            lang__iso__in=['es', 'zh-SG', 'zh-TW']
        ).delete()
        # missing some data so nothing should change
        self._add_missing_datalogs()
        self._check_filter(BOEvent, EventCompleteFilter, 'complete', 0, nb_data)
        self._add_missing_datas()
        self._check_filter(BOEvent, EventCompleteFilter, 'complete',
                           1, nb_data - 1)


# test event filters

    def test_10_filter_services(self):
        resp = self.api_client.get(self.url)
        datas = self.deserialize(resp)

        services = []
        nb_event = len(datas)
        for data in datas:
            services.extend(data['services'])
        services = set(services)
        self.assertEqual(len(services), len(BOService.SERVICE_CHOICES))

        resp = self.api_client.get('%s?services=PAAS' % self.url)
        datas = self.deserialize(resp)
        self.assertNotEqual(len(datas), 0)
        self.assertNotEqual(len(datas), nb_event)
        for data in datas:
            self.assertIn('PAAS', data['services'])

        resp = self.api_client.get('%s?services=IAAS&services=PAAS' % self.url)
        datas = self.deserialize(resp)
        self.assertNotEqual(len(datas), 0)
        self.assertNotEqual(len(datas), nb_event)
        for data in datas:
            if not 'PAAS' in data['services']:
                self.fail('PAAS not found in services')

        resp = self.api_client.get('%s?services=IaAs&services=pAaS' % self.url)
        datas = self.deserialize(resp)
        self.assertNotEqual(len(datas), 0)
        self.assertNotEqual(len(datas), nb_event)
        for data in datas:
            if not 'PAAS' in data['services']:
                self.fail('PAAS not found in services')

    def test_11_filter_category(self):
        resp = self.api_client.get(self.url)
        datas = self.deserialize(resp)

        categories = []
        nb_event = len(datas)
        for data in datas:
            categories.append(data['category'])
        categories = set(categories)
        self.assertEqual(len(categories), len(BOEvent.CATEGORY_CHOICES))

        resp = self.api_client.get('%s?category=Incident' % self.url)
        datas = self.deserialize(resp)
        self.assertNotEqual(len(datas), 0)
        self.assertNotEqual(len(datas), nb_event)
        for data in datas:
            self.assertEqual(data['category'], 'Incident')

        resp = self.api_client.get('%s?category=inCIdeNT' % self.url)
        datas = self.deserialize(resp)
        self.assertNotEqual(len(datas), 0)
        self.assertNotEqual(len(datas), nb_event)
        for data in datas:
            self.assertEqual(data['category'], 'Incident')

    def test_12_filter_date_end_null(self):
        url = '%s?date_end=null' % self.url

        resp = self.api_client.get(url)
        datas = self.deserialize(resp)
        self.assertEqual(len(datas), 0)

        event = self._create_event(42, [BOService.PAAS], BOEvent.INCIDENT)
        resp = self.api_client.get(url)
        datas = self.deserialize(resp)
        self.assertEqual(len(datas), 1)

        event.end()
        resp = self.api_client.get(url)
        datas = self.deserialize(resp)
        self.assertEqual(len(datas), 0)

    def test_13_filter_current(self):
        url = '%s?current=true' % self.url

        resp = self.api_client.get(url)
        datas = self.deserialize(resp)
        self.assertEqual(len(datas), 0)

        event = self._create_event(42, [BOService.PAAS], BOEvent.INCIDENT)
        resp = self.api_client.get(url)
        datas = self.deserialize(resp)
        self.assertEqual(len(datas), 1)

        event.end()
        resp = self.api_client.get(url)
        datas = self.deserialize(resp)
        self.assertEqual(len(datas), 0)
