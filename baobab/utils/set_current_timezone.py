# -*- coding: utf-8 -*-

import pytz

from django.conf import settings
from django.utils import timezone


class TimezoneMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated():
            timezone.activate(pytz.timezone(str(request.user.timezone)))
        else:
            timezone.activate(settings.TIME_ZONE)
