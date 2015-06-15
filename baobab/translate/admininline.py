# -*- coding: utf-8 -*-

"""
all the inline class
"""

from baobab.utils.admin import TabularInline
from baobab.translate import models
from baobab.translate.adminform import EventDataForm, EventLogDataForm


class EventDataInline(TabularInline):
    form = EventDataForm
    model = models.EventData
    fields = ['lang', 'title', 'summary']
    extra = models.Lang.count()
    max_num = extra

    # XXX for safety
    def has_delete_permission(self, request, obj=None):
        return False


class EventLogDataInline(TabularInline):
    form = EventLogDataForm
    model = models.EventLogData
    fields = ['lang', 'comment']
    extra = models.Lang.count()
    max_num = extra

    # XXX for safety
    def has_delete_permission(self, request, obj=None):
        return False
