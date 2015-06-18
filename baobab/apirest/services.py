# -*- coding: utf-8 -*-
"""
API REST for baobab
"""
from baobab.backoffice.models import Service as BOService

from baobab.apirest.modelresource import RawModelResource
from baobab.apirest.status import StatusResource


class ServicesResource(RawModelResource):

    def dehydrate(self, bundle):
        bundle.data['name'] = bundle.obj.get_name_display()
        bundle.data['status'] = bundle.obj.get_status_display()
        return bundle

    def build_schema(self):
        """
        dehydrate overwrite some value need to manually fix the schema
        """
        from baobab.apirest.urls import ApiUrls

        schema = super(ServicesResource, self).build_schema()
        schema['fields']['name']['type'] = 'string'
        schema['fields']['status'] = {
            'type': 'related',
            'schema': '/%s/%s/schema' % (ApiUrls.name,
                                         StatusResource._meta.resource_name)
        }
        return schema

    class Meta(RawModelResource.Meta):
        queryset = BOService.objects.all()
        excludes = ['id', ]
