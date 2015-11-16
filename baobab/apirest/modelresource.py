# -*- coding: utf-8 -*-
"""
This class override the tastypie's ModelResource class

 - remove the meta object
 - remove the encapsulated data inside a sub objects
 - disable the page: no limit on the query
 - remove the resource_uri field

"""

import textwrap
import pytz
import json

from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponse
from django.utils.timezone import is_naive

from tastypie.exceptions import (UnsupportedFormat,
                                 ImmediateHttpResponse, NotFound)
from tastypie.http import HttpNotImplemented, HttpApplicationError

try:
    from tastypie.http import HttpNotFound
except ImportError:
    # tastypie <= 0.9.10
    class HttpNotFound(HttpResponse):
        status_code = 404

from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie.bundle import Bundle


def my_handler(obj):
    """
    handle Bundle tastypie obj (Bundle might be nested)
    handle datetime formatting
    """
    if isinstance(obj, Bundle):
        obj = obj.data
    if hasattr(obj, 'isoformat'):
        return MySerializer.format_datetime(obj)
    return obj


class MySerializer(Serializer):

    """
    always return UTC datetimes in ISO 8601
    """

    @classmethod
    def format_datetime(cls, date):
        if is_naive(date):
            date = pytz.timezone(settings.TIME_ZONE).localize(date)
        if not isinstance(date.tzinfo, pytz.UTC.__class__):
            date = date.astimezone(pytz.UTC)
        # XXX date set in the admin doesn't have microsecond, but the one set
        #     with 'default=now' has, for consistency never output microsecond
        return date.replace(microsecond=0).isoformat()

    def to_html(self, data, options=None):
        if isinstance(data, dict) and 'fields' in data:
            title = settings.TITLE_SCHEMA
        else:
            title = settings.TITLE_RESULT
        return textwrap.dedent("""
        <!DOCTYPE html>
        <html>
          <head>
            <style>
              body {
                font-family: Monaco,"DejaVu Sans Mono",
                             "Courier New",monospace;
              }
              div {
                margin: 5px;
                padding: 5px;
                border: 1px solid #444;
                border-radius: 5px;
                background-color: #eee;
              }
              h1 {
                font-size: 1.4rem;
              }
              .command:before {
                font-size: 1.4rem;
              }
              pre {
                white-space: pre-wrap;
              }
            </style>
            <title>%(title)s</title>
          </head>
          <body>
            <div>
              <h1 class="command">%(title)s</h1>
              <pre>%(data)s</pre>
            </div>
          </body>
        </html>
        """) % {
            'title': title,
            'data': json.dumps(data, indent=4, sort_keys=True,
                               default=my_handler)
        }

    def serialize(self, bundle, format='application/json', options={}):
        try:
            return super(MySerializer, self).serialize(bundle, format, options)
        except (ImproperlyConfigured, UnsupportedFormat):
            raise ImmediateHttpResponse(
                HttpNotImplemented(settings.HTTP_NOT_IMPLEMENTED_ERROR)
            )
        except ImmediateHttpResponse:
            raise
        except Exception:
            raise ImmediateHttpResponse(
                HttpApplicationError(settings.HTTP_APPLICATION_ERROR)
            )


class RawModelResource(ModelResource):

    def accept_languages(self, request):
        if not request:
            return ['en', ]

        if hasattr(request, 'accept_languages'):
            return request.accept_languages

        accept_languages = []
        for lang in request.META.get('HTTP_ACCEPT_LANGUAGE', '').split(','):
            lang = lang.strip().split(';')[0]
            accept_languages.append(lang)
            accept_languages.append(lang.split('-')[0])
        accept_languages.append('en')
        setattr(request, 'accept_languages', accept_languages)
        return accept_languages

    def add_content_language(self, request, lang):
        if not request:
            return
        if not hasattr(request, 'content_language'):
            setattr(request, 'content_language', [])
        request.content_language.append(lang)

    def create_response(self, request, data, **response_kwargs):
        """
        to set the Content-Language Header
        """
        response = super(RawModelResource, self).create_response(
            request, data, **response_kwargs)

        if hasattr(response, '__setitem__'):
            content_language = getattr(request, 'content_language', None)
            if content_language and len(set(content_language)) == 1:
                response['Content-Language'] = content_language[0]
            if hasattr(request, 'total_count'):
                response['X-Total-Count'] = getattr(request, 'total_count')
        return response

    def alter_list_data_to_serialize(self, request, data_dict):
        if data_dict['meta'].get('total_count'):
            setattr(request, 'total_count', data_dict['meta']['total_count'])
        return data_dict['objects']

    def build_schema(self):
        schema = super(RawModelResource, self).build_schema()
        for key in schema['fields']:
            if schema['fields'][key]['type'] == 'datetime':
                schema['fields'][key]['help_text'] = \
                    'UTC datetimes in ISO 8601'
            if key == 'id':
                schema['fields'][key]['help_text'] = 'Id of the elem'
                schema['fields'][key]['type'] = 'integer'
            if 'default' in schema['fields'][key]:
                del schema['fields'][key]['default']
        return schema

    def obj_get(self, **kwargs):
        try:
            return super(RawModelResource, self).obj_get(**kwargs)
        except (NotFound, ObjectDoesNotExist):
            raise ImmediateHttpResponse(
                HttpNotFound(settings.HTTP_NOT_FOUND)
            )
        except ImmediateHttpResponse:
            raise
        except Exception:
            raise ImmediateHttpResponse(
                HttpApplicationError(settings.HTTP_APPLICATION_ERROR)
            )

    def obj_get_list(self, **kwargs):
        try:
            return super(RawModelResource, self).obj_get_list(**kwargs)
        except (NotFound, ObjectDoesNotExist):
            raise ImmediateHttpResponse(
                HttpNotFound(settings.HTTP_NOT_FOUND)
            )
        except ImmediateHttpResponse:
            raise
        except Exception:
            raise ImmediateHttpResponse(
                HttpApplicationError(settings.HTTP_APPLICATION_ERROR)
            )

    class Meta:
        max_limit = None
        include_resource_uri = False
        allowed_methods = ['get']
        serializer = MySerializer()
