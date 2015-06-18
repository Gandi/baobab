# -*- coding: utf-8 -*-
"""
To define the url for the API
"""

import textwrap
import json

from django.http import HttpResponse

from tastypie.api import Api
from tastypie.exceptions import BadRequest
from tastypie.utils import is_valid_jsonp_callback_value
from tastypie.utils.mime import determine_format, build_content_type
from tastypie.serializers import Serializer

from baobab.apirest.events import EventsResource
from baobab.apirest.services import ServicesResource
from baobab.apirest.status import StatusResource


class MyApi(Api):

    def top_level(self, request, api_name=None):
        """
        this is a copy/past of the method Api.top_level
        the original method locally use a Serializer object which didn't
        implement the `to_html` method
        this function does exactly the same except it can server html content
        """

        serializer = Serializer()
        available_resources = {}

        if api_name is None:
            api_name = self.api_name

        for name in sorted(self._registry.keys()):
            kwargs = {
                'api_name': api_name,
                'resource_name': name,
            }
            available_resources[name] = {
                'list_endpoint': self._build_reverse_url("api_dispatch_list",
                                                         kwargs=kwargs),
                'schema': self._build_reverse_url("api_get_schema",
                                                  kwargs=kwargs),
            }

        desired_format = determine_format(request, serializer)
        options = {}
        if 'text/html' in desired_format:
            serialized = textwrap.dedent("""
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
                </style>
              </head>
              <title>Api route</title>
              <body>
                <div>
                  <h1 class="command">Available route</h1>
                  <pre>%s</pre>
                </div>
              </body>
            </html>
            """) % json.dumps(available_resources, indent=4, sort_keys=True)
        else:
            if 'text/javascript' in desired_format:
                callback = request.GET.get('callback', 'callback')
                if not is_valid_jsonp_callback_value(callback):
                    raise BadRequest('JSONP callback name is invalid.')
                options['callback'] = callback
            serialized = serializer.serialize(available_resources,
                                              desired_format, options)
        return HttpResponse(content=serialized,
                            content_type=build_content_type(desired_format))


class ApiUrls(object):

    name = 'api'

    @classmethod
    def get_urls(cls):
        api_name = MyApi(api_name=cls.name)
        api_name.register(EventsResource())
        api_name.register(ServicesResource())
        api_name.register(StatusResource())
        return api_name.urls
