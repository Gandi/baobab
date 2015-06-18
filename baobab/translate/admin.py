# -*- coding: utf-8 -*-
"""
Define the form for django's admin
"""

from django.contrib import admin

from baobab.utils.admin import ModelAdmin

from baobab.translate.models import Lang, Event, EventLog
from baobab.translate.admininline import EventDataInline, EventLogDataInline
from baobab.translate.adminfilter import (EventCompleteFilter,
                                          EventLogCompleteFilter)


class EventAdmin(ModelAdmin):
    fields = ['title_en', ]
    readonly_fields = ['title_en', ]
    list_display = ['title_en', 'complete_event', 'complete_log']
    list_display_dynamic = {
        'val_name': Lang.objects.exclude(iso='en').values_list('iso', 'name'),
        'filter': 'lang__iso',
        'sub_obj': 'eventdatas',
    }
    inlines = [EventDataInline, ]
    list_filter = [EventCompleteFilter, ]
    search_fields = ['eventdatas__title']

    def title_en(self, obj):
        return obj.eventdatas.get(lang__iso='en').title
    title_en.short_description = 'Title'

    def complete_event(self, obj):
        if obj.eventdatas.count() == Lang.objects.count():
            return '<b>True<b>'
        return 'False'
    complete_event.allow_tags = True

    def complete_log(self, obj):
        for eventlog in obj.eventlogs.all():
            if eventlog.eventlogdatas.count() != Lang.objects.count():
                return 'False'
        return '<b>True<b>'
    complete_log.allow_tags = True

    # XXX for safety
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name='translate').exists():
            return True
        return super(EventAdmin, self).has_change_permission(request, obj=obj)


class EventLogAdmin(ModelAdmin):
    fields = ['comment_en', ]
    readonly_fields = ['comment_en', ]
    list_display = ['title_en', 'comment_en', 'complete']
    list_display_dynamic = {
        'val_name': Lang.objects.exclude(iso='en').values_list('iso', 'name'),
        'filter': 'lang__iso',
        'sub_obj': 'eventlogdatas',
    }
    inlines = [EventLogDataInline, ]
    list_filter = [EventLogCompleteFilter, ]
    search_fields = ['event__eventdatas__title']

    def title_en(self, obj):
        return obj.event.eventdatas.get(lang__iso='en').title
    title_en.short_description = 'Title'

    def comment_en(self, obj):
        return obj.eventlogdatas.get(lang__iso='en').comment
    comment_en.short_description = 'Comment'

    def complete(self, obj):
        if obj.eventlogdatas.count() == Lang.objects.count():
            return '<b>True<b>'
        return 'False'
    complete.allow_tags = True

    # XXX for safety
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name='translate').exists():
            return True
        return super(EventLogAdmin, self).has_change_permission(request,
                                                                obj=obj)


admin.site.register(Event, EventAdmin)
admin.site.register(EventLog, EventLogAdmin)
