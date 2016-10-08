# -*- coding: utf-8 -*-
"""
API REST for baobab
"""
import logging

from django.conf.urls import url
from django.db.models import Q
from django.utils.timezone import now

from tastypie import fields
from tastypie.resources import ALL_WITH_RELATIONS
from tastypie.utils import trailing_slash
from tastypie.exceptions import BadRequest
from tastypie.http import HttpBadRequest

from baobab.backoffice.models import (Event as BOEvent,
                                      Service as BOService)
from baobab.apirest.modelresource import RawModelResource
from baobab.apirest.services import ServicesResource

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


class ServicesLinkedResource(RawModelResource):

    """
    used by the EventsResource to be able to filter by services
    """

    def dehydrate(self, bundle):
        """
        only need the name of the service
        """
        return bundle.obj.get_name_display()

    class Meta(RawModelResource.Meta):
        queryset = BOService.objects.all()
        filtering = {
            'name': ['exact', 'in'],
        }


class EventsResource(RawModelResource):

    """
    used when querying a list
    return the list of event
    """

    services = fields.ToManyField(
        ServicesLinkedResource,
        'services',
        full=True,
    )
    service_choices = dict((v.upper(), str(k))
                           for k, v in BOService.SERVICE_CHOICES)
    category_choices = dict((v.upper(), str(k))
                            for k, v in BOEvent.CATEGORY_CHOICES)

    def build_filters(self, filters=None):
        """
        To be able to filter using the name (string) instead of the value (int)
        """
        if not filters:
            filters = {}

        for key, val in filters.items():
            if key.startswith('services'):
                try:
                    tmp = self.service_choices[val.upper()]
                except KeyError:
                    list_ = ', '.join(self.service_choices)
                    raise BadRequest({
                        'error': "'{}' not in list: {}".format(val, list_),
                        'field': 'services',
                    })
                del filters[key]
                key = key.split('__', 1)
                key.insert(1, 'name')
                filters['__'.join(key)] = tmp
            if key == 'category':
                try:
                    filters[key] = self.category_choices[val.upper()]
                except KeyError:
                    list_ = ', '.join(self.category_choices)
                    raise BadRequest({
                        'error': "'{}' not in list: {}".format(val, list_),
                        'field': 'category',
                    })
            if key == 'date_end' and val.lower() == 'null':
                del filters['date_end']
                filters['date_end__isnull'] = True

        if 'current' in filters:
            del filters['current']

        return super(EventsResource, self).build_filters(filters)

    # XXX simulate the apply_filters only avaialbe with Tastypie > 0.9.10
    def get_object_list(self, request):
        current = request.GET.get('current')
        if current:
            val = current.lower()
            if val not in ('true', 'false'):
                raise BadRequest({
                    'error': "choises are: ['true', 'false']",
                    'field': 'current',
                })
            for key in request.GET:
                if 'date' in key:
                    raise BadRequest({
                        'error': "Can't be used in the same time as 'current'",
                        'field': 'date',
                    })
            current = ((Q(date_end__isnull=True) | Q(date_end__gt=now)) &
                       Q(date_start__lte=now))
            if val == 'false':
                current = ~current
        objs = super(EventsResource, self).get_object_list(request)
        if current:
            return objs.filter(current)
        return objs

    def build_schema(self):
        from baobab.apirest.urls import ApiUrls

        schema = super(EventsResource, self).build_schema()
        schema['fields']['category']['value'] = \
            [val[1] for val in BOEvent.CATEGORY_CHOICES]
        schema['fields']['services']['schema'] = '/%s/%s/schema' % (
            ApiUrls.name, ServicesResource._meta.resource_name)
        schema['fields']['estimate_date_end'] = {
            'help_text':
                'UTC datetimes in ISO 8601 (use when an incident is ongoing)',
            'nullable': False,
            'readonly': True,
            'type': 'string',
        }
        schema['fields']['summary'] = {
            'help_text': 'More information about the event',
            'nullable': False,
            'readonly': True,
            'only_in_detail_view': True,
            'type': 'string',
        }
        schema['fields']['logs'] = {
            'help_text': 'Complementary information adding during the event',
            'nullable': False,
            'readonly': True,
            'only_in_detail_view': True,
            'type': 'list of dict',
            'dict': {
                'comment': {
                    'help_text':
                        'Complementary information adding during the event',
                    'type': 'string'
                },
                'date': {
                    'help_text': 'UTC datetimes in ISO 8601',
                    'nullable': False,
                    'readonly': True,
                    'type': 'string'
                },
            },
        }
        schema['filtering']['services'] = ['exact', 'in']
        schema['filtering']['current'] = ['exact', ]
        return schema

    # XXX should be done with a use_in but need tastypie >= 0.9.16
    def prepend_urls(self):
        """
        override the uri for one event to be able to add some information
        """
        return [
            url(r"^(?P<resource_name>%s)%s/$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r'^(?P<resource_name>%s)/(?P<pk>\d*)%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_event_detail'),
                name='api_get_event_detail'),
        ]

    def override_urls(self):
        return self.prepend_urls()

    def get_event_detail(self, request, **kwargs):
        return EventResource().get_detail(request, pk=int(kwargs['pk']))

    def dehydrate(self, bundle):
        bundle.data['title'] = {}
        if 'summary' in self._meta.fields:
            bundle.data['summary'] = {}
        for data in bundle.obj.eventdatas.all():
            bundle.data['title'][data.lang.iso] = data.title
            if 'summary' in self._meta.fields:
                bundle.data['summary'][data.lang.iso] = data.summary
        # XXX fallback should be remove
        if not len(bundle.data['title']):
            LOG.error('error when dehydrating an eventdata: %s',
                      bundle.data['id'])
            bundle.data['title']['en'] = bundle.obj.title
            if 'summary' in self._meta.fields:
                bundle.data['summary']['en'] = bundle.obj.summary
        bundle.data['category'] = bundle.obj.get_category_display()
        return bundle

    def alter_list_data_to_serialize(self, request, data_dict):
        data_dict = super(EventsResource,
                          self).alter_list_data_to_serialize(request,
                                                             data_dict)
        res = []
        for data in data_dict:
            res.append(self.alter_detail_data_to_serialize(request, data))
        return res

    def alter_detail_data_to_serialize(self, request, data_dict):
        """
        filter the title/summary to only get the one set in Accept_Language
        """
        data_dict = super(EventsResource,
                          self).alter_detail_data_to_serialize(request,
                                                               data_dict)
        for lang in self.accept_languages(request):
            if lang in data_dict.data['title']:
                self.add_content_language(request, lang)
                data_dict.data['title'] = data_dict.data['title'][lang]
                if 'summary' in self._meta.fields:
                    data_dict.data['summary'] = data_dict.data['summary'][lang]
                return data_dict
        # XXX we should never get here it's just for safety
        LOG.warn('No languages matched for eventdata: %d, falling back to en',
                 data_dict.data['id'])
        data_dict.data['title'] = data_dict.data['title']['en']
        if 'summary' in self._meta.fields:
            data_dict.data['summary'] = data_dict.data['summary']['en']

    class Meta(RawModelResource.Meta):
        excludes = ['summary', ]
        allowed_methods = ['get', ]
        queryset = BOEvent.objects.prefetch_related(
            'services',
            'eventdatas',
        ).all()
        filtering = {
            'date_end': ['exact', 'range', 'gt', 'gte', 'lt', 'lte', 'isnull'],
            'date_start': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
            'estimate_date_end': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
            'last_update': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
            'services': ALL_WITH_RELATIONS,
            'category': ['exact', ],
        }
        fields = ('category', 'date_end', 'date_start', 'duration',
                  'estimate_date_end', 'last_update', 'id', 'services')


class EventResource(EventsResource):

    """
    used when querying a specific object
    return the specified event with its log
    """

    def _get_log(self, eventlog):
        comment = {}
        for logdata in eventlog.eventlogdatas.all():
            comment[logdata.lang.iso] = logdata.comment
        # XXX fallback should be remove
        if not comment:
            LOG.error('error when dehydrating an eventlogdata: %s',
                      eventlog.id)
            comment['en'] = eventlog.comment
        return {
            'comment': comment,
            'date': eventlog.date,
            'id': eventlog.id,
        }

    def dehydrate(self, bundle):
        bundle = super(EventResource, self).dehydrate(bundle)
        bundle.data['logs'] = []
        for eventlog in bundle.obj.eventlogs.all():
            bundle.data['logs'].append(self._get_log(eventlog))
        return bundle

    def alter_detail_data_to_serialize(self, request, data_dict):
        """
        filter the comment to only get the one set in Accept_Language
        """
        data_dict = super(EventResource,
                          self).alter_detail_data_to_serialize(request,
                                                               data_dict)
        logs = []
        for log in data_dict.data['logs']:
            for lang in self.accept_languages(request):
                if lang in log['comment']:
                    self.add_content_language(request, lang)
                    log['comment'] = log['comment'][lang]
                    break
            else:
                # XXX we should never get here it's just for safety
                LOG.warn('No languages matched for eventlogdata: %d, '
                         'falling back to en', log.obj.id)
                log['comment'] = log['comment']['en']
            logs.append(log)
        data_dict.data['logs'] = logs
        return data_dict

    def build_schema(self):
        schema = super(EventResource, self).build_schema()
        schema.update({
            'logs': {
                'dict': {
                    'comment': {'help_text': ('Complementary information '
                                              'adding during the event'),
                                'type': 'string'},
                    'date': {'help_text': 'UTC datetimes in ISO 8601',
                             'nullable': False,
                             'readonly': True,
                             'type': 'string'},
                },
                'help_text': ('Complementary information '
                              'adding during the event'),
                'nullable': False,
                'only_in_detail_view': True,
                'readonly': True,
                'type': 'list of dict',
            },
        })
        return schema

    class Meta(RawModelResource.Meta):
        queryset = BOEvent.objects.prefetch_related(
            'services',
            'eventdatas',
            'eventlogs',
            'eventlogs__eventlogdatas',
        ).all()
        filtering = {
            'pk': 'exact',
        }
        allowed_methods = ['get', ]
        fields = EventsResource.Meta.fields + ('summary', )
