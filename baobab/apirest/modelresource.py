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
import logging
import warnings

from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils.timezone import is_naive

# Django 1.5 has moved this constant up one level.
try:
    from django.db.models.constants import LOOKUP_SEP
except ImportError:
    from django.db.models.sql.constants import LOOKUP_SEP

import tastypie
from tastypie.exceptions import (UnsupportedFormat, NotFound, BadRequest,
                                 InvalidFilterError, InvalidSortError)
from tastypie.http import HttpApplicationError, HttpNotImplemented
from tastypie import http
from tastypie.resources import ALL, ALL_WITH_RELATIONS

try:
    from tastypie.http import HttpNotFound
except ImportError:
    # tastypie <= 0.9.10
    class HttpNotFound(HttpResponse):
        status_code = 404

from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie.bundle import Bundle

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


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
            raise HttpNotImplemented(settings.HTTP_NOT_IMPLEMENTED_ERROR)


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

    # overwrite some method to have the same 'json' schema return for all
    # kind of error

    def _handle_500(self, request, exception):
        response_class = HttpApplicationError
        response_code = 500
        if isinstance(exception, (NotFound, ObjectDoesNotExist, Http404)):
            response_class = HttpResponseNotFound
            response_code = 404

        LOG.error('Internal Server Error: %s' % request.path, exc_info=True,
                  extra={'status_code': response_code, 'request': request})

        if settings.DEBUG:
            import traceback
            import sys
            tb = '\n'.join(traceback.format_exception(*(sys.exc_info())))
            data = {
                "error": unicode(exception),
                "traceback": tb,
            }
            return self.error_response(request, data,
                                       response_class=response_class)

        msg = "Sorry, this request could not be processed. " \
              "Please try again later."
        data = {
            'error': getattr(settings, 'HTTP_APPLICATION_ERROR', msg),
        }
        return self.error_response(request, data,
                                   response_class=response_class)

    def error_response(self, request, errors, response_class=None):
        desired_format = self._meta.default_format
        if request:
            try:
                desired_format = self.determine_format(request)
            except BadRequest:
                pass

        if response_class is None:
            response_class = http.HttpBadRequest

        if isinstance(errors, dict) and 'error' in errors:
            errors = errors['error']
        if isinstance(errors, basestring):
            errors = {'error': errors}

        serialized = self.serialize(request, errors, desired_format)
        return response_class(content=serialized, content_type=desired_format)

    def check_filtering(self, field_name, filter_type='exact',
                        filter_bits=None):
        """
        Given a field name, a optional filter type and an optional list of
        additional relations, determine if a field can be filtered on.

        If a filter does not meet the needed conditions, it should raise an
        ``InvalidFilterError``.

        If the filter meets the conditions, a list of attribute names (not
        field names) will be returned.
        """
        if filter_bits is None:
            filter_bits = []

        if field_name not in self._meta.filtering:
            raise InvalidFilterError({
                'error': ("Filtering on '{}' is not allowed."
                          "".format(field_name)),
                'field': field_name,
            })

        # Check to see if it's an allowed lookup type.
        if not self._meta.filtering[field_name] in (ALL, ALL_WITH_RELATIONS):
            # Must be an explicit whitelist.
            if filter_type not in self._meta.filtering[field_name]:
                raise InvalidFilterError({
                    'error': ("Filter '{}' is not allowed on field '{}'"
                              "".format(filter_type, field_name)),
                    'field': field_name,
                })
        if self.fields[field_name].attribute is None:
            raise InvalidFilterError({
                'error': ("The '{}' field has no 'attribute' for "
                          "searching with.".format(field_name)),
                'field': field_name,
            })

        # Check to see if it's a relational lookup and if that's allowed.
        if len(filter_bits):
            if not getattr(self.fields[field_name], 'is_related', False):
                raise InvalidFilterError({
                    'error': ("The '{}' field does not support relations."
                              "".format(field_name)),
                    'field': field_name,
                })

            if not self._meta.filtering[field_name] == ALL_WITH_RELATIONS:
                raise InvalidFilterError({
                    'error': ("Lookups are not allowed more than one level "
                              "deep on the '{}' field.".format(field_name)),
                    'field': field_name,
                })

            # Recursively descend through the remaining lookups in the filter,
            # if any. We should ensure that all along the way, we're allowed
            # to filter on that field by the related resource.
            resource = self.fields[field_name]
            related_resource = resource.get_related_resource(None)
            return [resource.attribute] + \
                related_resource.check_filtering(filter_bits[0], filter_type,
                                                 filter_bits[1:])

        return [self.fields[field_name].attribute]

    def apply_sorting(self, obj_list, options=None):
        """
        Given a dictionary of options, apply some ORM-level sorting to the
        provided ``QuerySet``.

        Looks for the ``order_by`` key and handles either ascending (just the
        field name) or descending (the field name with a ``-`` in front).

        The field name should be the resource field, **NOT** model field.
        """
        if options is None:
            options = {}

        parameter_name = 'order_by'

        if 'order_by' not in options:
            if 'sort_by' not in options:
                # Nothing to alter the order. Return what we've got.
                return obj_list
            else:
                warnings.warn("'sort_by' is a deprecated parameter. "
                              "Please use 'order_by' instead.")
                parameter_name = 'sort_by'

        order_by_args = []

        if hasattr(options, 'getlist'):
            order_bits = options.getlist(parameter_name)
        else:
            order_bits = options.get(parameter_name)

            if not isinstance(order_bits, (list, tuple)):
                order_bits = [order_bits]

        for order_by in order_bits:
            order_by_bits = order_by.split(LOOKUP_SEP)

            field_name = order_by_bits[0]
            order = ''

            if order_by_bits[0].startswith('-'):
                field_name = order_by_bits[0][1:]
                order = '-'

            if field_name not in self.fields:
                # It's not a field we know about. Move along citizen.
                raise InvalidSortError({
                    'error': ("No matching '{}' field for ordering on."
                              "".format(field_name)),
                    'field': field_name,
                })

            if field_name not in self._meta.ordering:
                raise InvalidSortError({
                    'error': ("The '{}' field does not allow ordering."
                              "".format(field_name)),
                    'field': field_name,
                })

            if self.fields[field_name].attribute is None:
                raise InvalidSortError({
                    'error': ("The '{}' field has no 'attribute' for "
                              "ordering with.".format(field_name)),
                    'field': field_name,
                })

            order_by_args.append("%s%s" % (order, LOOKUP_SEP.join([
                self.fields[field_name].attribute] + order_by_bits[1:])))

        return obj_list.order_by(*order_by_args)

    if tastypie.__version__ < (0, 9, 12):

        # this in need to hanble the error for thoes versions

        def wrap_view(self, view):

            try:
                from django.views.decorators.csrf import csrf_exempt
            except ImportError:
                def csrf_exempt(func):
                    return func

            @csrf_exempt
            def wrapper(request, *args, **kwargs):
                from django.utils.cache import patch_cache_control
                from tastypie.fields import ApiFieldError
                from django.core.exceptions import ValidationError

                try:
                    callback = getattr(self, view)
                    response = callback(request, *args, **kwargs)

                    if request.is_ajax():
                        patch_cache_control(response, no_cache=True)

                    return response
                except (BadRequest, ApiFieldError, InvalidSortError) as e:
                    data = {"error": e.args[0] if getattr(e, 'args') else ''}
                    return self.error_response(
                        request, data, response_class=http.HttpBadRequest)
                except ValidationError, e:
                    data = {"error": e.messages}
                    return self.error_response(
                        request, data, response_class=http.HttpBadRequest)
                except Exception, e:
                    if hasattr(e, 'response'):
                        return e.response

                    # A real, non-expected exception.
                    # Handle the case where the full traceback is more helpful
                    # than the serialized error.
                    if settings.DEBUG and getattr(
                            settings, 'TASTYPIE_FULL_DEBUG', False):
                        raise

                    # Re-raise the error to get a proper traceback when the
                    # error happend during a test case
                    if request.META.get('SERVER_NAME') == 'testserver':
                        raise

                    # Rather than re-raising, we're going to things similar to
                    # what Django does. The difference is returning a
                    # serialized error message.
                    return self._handle_500(request, e)

            return wrapper

    class Meta:
        max_limit = None
        include_resource_uri = False
        allowed_methods = ['get']
        serializer = MySerializer()
