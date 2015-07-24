# -*- coding: utf-8 -*-
"""
Define the form for django's admin
"""
import datetime
import logging

from django.contrib import admin

from baobab.utils.admin import ModelAdmin

from baobab.translate.models import (Lang as TranslateLang,
                                     EventData as TranslateEventData,
                                     EventLogData as TranslateEventLogData)

from baobab.backoffice import models
from baobab.backoffice.admininline import EventLogInline
from baobab.backoffice.adminform import EventForm, EventLogForm

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


class EventAdmin(ModelAdmin):
    form = EventForm
    list_display = ['title_en', 'date_start', 'date_end', 'estimate_date_end',
                    'last_update', 'get_duration', 'first_user', 'last_user',
                    'category']
    list_display_dynamic = {
        'val_name': models.Service.SERVICE_CHOICES,
        'filter': 'name',
        'sub_obj': 'services',
    }
    inlines = [EventLogInline, ]

    search_fields = ['eventdatas__title']

    def changelist_view(self, request, extra_context=None):
        # XXX to keep compatibility: should be remove in a next release
        try:
            return super(EventAdmin, self).changelist_view(
                request=request, extra_context=extra_context)
        except Exception as err:
            LOG.error('error when searching an event: %s', err)
            self.search_fields = ['title']
            return super(EventAdmin, self).changelist_view(
                request=request, extra_context=extra_context)

    list_filter = ('services__name', 'date_start', 'last_update', 'category')
    fieldsets = [
        ('Real duration of the event ()',
         {'description': ("it used your browser's clock and will be converted "
                          'to UTC based on <a href="/admin/backoffice/'
                          'timezone/">your timezone</a>'),
          'fields': (('date_start', 'date_end'), )}),
        ('To define the estimated date end', {'fields': ('duration', )}),
        (None, {'fields': [('title_en', 'category'), ('summary_en', 'msg')]}),
        (None, {'fields': ('services', )}),
    ]

    def get_duration(self, obj):
        return datetime.timedelta(minutes=obj.duration)
    get_duration.short_description = 'duration'

    def title_en(self, obj):
        try:
            return obj.eventdatas.get(lang__iso='en').title
        except Exception as err:
            LOG.error("error when getting the event's title: %s", err)
            # XXX to keep compatibility: should be remove in a next release
            return obj.title

    def summary_en(self, obj):
        try:
            return obj.eventdatas.get(lang__iso='en').summary
        except Exception as err:
            LOG.error("error when getting the event's title: %s", err)
            # XXX to keep compatibility: should be remove in a next release
            return obj.summary

    def first_user(self, obj):
        if obj.eventlogs.count():
            # XXX no earliest before django 1.6
            return obj.eventlogs.order_by('date')[0].user.username.capitalize()
        else:
            return 'Unknown'
    first_user.short_description = 'user (first one)'

    def last_user(self, obj):
        if obj.eventlogs.count():
            return obj.eventlogs.latest('date').user.username.capitalize()
        else:
            return 'Unknown'
    last_user.short_description = 'user (last one)'


class EventLogAdmin(ModelAdmin):

    form = EventLogForm

    list_display = ('event', 'comment_en', 'date', 'user')
    fields = ('event', 'comment_en')

    def comment_en(self, obj):
        try:
            return obj.eventlogdatas.get(lang__iso='en').comment
        except:
            # XXX to keep compatibility: should be remove in a next release
            return obj.comment


class TimeZoneAdmin(ModelAdmin):
    list_display = ('timezone', )
    fields = ('timezone', )

    def queryset(self, request):
        qs = super(TimeZoneAdmin, self).queryset(request)
        return qs.filter(user=request.user)

    def has_add_permission(self, request):
        return False


admin.site.register(models.Event, EventAdmin)
admin.site.register(models.EventLog, EventLogAdmin)
admin.site.register(models.TimeZone, TimeZoneAdmin)
