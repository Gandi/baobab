# -*- coding: utf-8 -*-
"""
override the default manager
"""
from django.db import models
from django.db.models.query import QuerySet


class EventQuerySet(QuerySet):

    """
    The admin will always order the result
      (see dkago/contrib/admin/views/main.py ling 260)

    It will keep the right order and avoid the admin to do a -pk order
    """

    def order_by(self, *field_names):
        # XXX this is an 'impossible' filter, thus it still
        #     allow an other ordering if needed/wanted
        if set(field_names) == set(['id', 'pk']):
            return self._clone()
        return super(EventQuerySet, self).order_by(*field_names)


class EventManager(models.Manager):

    """
    manager for the event model

    get_query_set will always be called which is not the case for the
    others function (like all, filter) when they are chained
    """

    def get_query_set(self):
        return EventQuerySet(self.model, using=self._db).extra(
            select={'real_date_end': 'COALESCE(date_end, estimate_date_end)'},
            order_by=['-real_date_end', '-date_start'],
        )
