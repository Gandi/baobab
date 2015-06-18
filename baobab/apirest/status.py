# -*- coding: utf-8 -*-
"""
API REST for baobab
"""
from django.db.models import Q
from django.utils.timezone import now

from baobab.backoffice.models import (Event as BOEvent,
                                      Service as BOService)

from baobab.apirest.modelresource import RawModelResource


class StatusResource(RawModelResource):

    def alter_list_data_to_serialize(self, request, data_dict):
        """
        dehydrate will be call for each BOEvent
        here we need to compute the result of each event thus the use of
        this method instead of dehydrate

        the rule are:
          INCIDENT with impact on services = STORMY
          INCIDENT with no impact on services = FOGGY
          MAINTENANCE = CLOUDY
          OTHER = SUNNY

        """
        status = [BOService.SUNNY, ]
        for event in data_dict['objects']:  # data_dict is a tastypie Bundle
            event = event.obj
            if event.category == BOEvent.INCIDENT:
                if event.services.exists():
                    status.append(BOService.STORMY)
                else:
                    status.append(BOService.FOGGY)
            else:
                status.append(BOService.CLOUDY)
        return {'status':  BOService.DICT_STATUS_CHOICES[max(status)]}

    def build_schema(self):
        """
        due to the use of alter_list_data_to_serialize need to manually
        create the schema
        """
        return {
            "allowed_detail_http_methods": [
                None
            ],
            "allowed_list_http_methods": [
                "get"
            ],
            "default_format": "application/json",
            "fields": {
                "status": {
                    "help_text": "the status of Gandi's platform",
                    "nullable": False,
                    "readonly": True,
                    "type": "string",
                    "value": [{status[1]: status[2]}
                              for status in BOService.STATUS_CHOICES]
                },
            },
        }

    def get_object_list(self, request):
        return super(StatusResource, self).get_object_list(request).filter(
            Q(date_end__isnull=True) | Q(date_end__gt=now),
            date_start__lte=now
        )

    class Meta(RawModelResource.Meta):
        queryset = BOEvent.objects.all()
        detail_allowed_methods = []  # disable all request on specific resource
