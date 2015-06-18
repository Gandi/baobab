from urlparse import urlparse
import re

from django.http import HttpResponse

ACCESS_CONTROL_ALLOW_ORIGIN = 'Access-Control-Allow-Origin'
ACCESS_CONTROL_EXPOSE_HEADERS = 'Access-Control-Expose-Headers'
ACCESS_CONTROL_ALLOW_CREDENTIALS = 'Access-Control-Allow-Credentials'
ACCESS_CONTROL_ALLOW_HEADERS = 'Access-Control-Allow-Headers'
ACCESS_CONTROL_ALLOW_METHODS = 'Access-Control-Allow-Methods'
ACCESS_CONTROL_MAX_AGE = 'Access-Control-Max-Age'

CORS_URLS_REGEX = r'^/api/.*$'
CORS_ALLOW_METHODS = ['GET']


class CorsMiddleware(object):

    def process_request(self, request):
        '''
            If CORS preflight header, then create an empty body response (200 OK) and return it

            Django won't bother calling any other request view/exception middleware along with
            the requested view; it will call any response middlewares
        '''
        if (request.method == 'OPTIONS' and
                'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META):
            response = HttpResponse()
            return response
        return None

    def process_response(self, request, response):
        '''
            Add the respective CORS headers
        '''
        origin = request.META.get('HTTP_ORIGIN')
        if origin:
            # todo: check hostname from db instead
            url = urlparse(origin)

            if not re.match(CORS_URLS_REGEX, request.path):
                return response

            response[ACCESS_CONTROL_ALLOW_ORIGIN] = "*"
            response[ACCESS_CONTROL_ALLOW_METHODS] = ', '.join(
                CORS_ALLOW_METHODS)

        return response
