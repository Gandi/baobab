# -*- coding: utf-8 -*-

"""
Re-define some default admin form
"""

import logging
import math

from django.conf import settings
from django.forms import ModelForm, CheckboxSelectMultiple, Textarea, CharField
from django.forms.util import ErrorDict

from baobab.translate.models import Lang as TranslateLang
from baobab.translate.models import EventData as TranslateEventData
from baobab.translate.models import EventLogData as TranslateEventLogData
from baobab.backoffice import models
from baobab.socialnetwork import SocialNetworks

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


class EventForm(ModelForm):
    title_en = CharField(max_length=255, label='Title',
                         help_text='A short description of the event')
    summary_en = CharField(required=False, widget=Textarea, label='Summary',
                           help_text='Support Markdown, show <a href="http://e'
                                     'n.wikipedia.org/wiki/Markdown#Example" t'
                                     'arget="_blank">documentation</a>')

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

        self.fields['title_en'].widget.attrs.update({'class': 'vTextField'})
        self.fields['summary_en'].widget.attrs.update(
            {'class': 'vLargeTextField'})

        if 'instance' in kwargs and kwargs['instance']:
            event = kwargs['instance']
            try:
                event_data = event.eventdatas.get(lang__iso='en')
                self.fields['title_en'].initial = event_data.title
                self.fields['summary_en'].initial = event_data.summary
            except Exception as err:
                LOG.error('error when initializing the EventForm: %s', err)
                # XXX to keep compatibility: should be remove in a next release
                self.fields['title_en'].initial = event.title
                self.fields['summary_en'].initial = event.summary

    def clean(self):
        """
        remove the mandatory on the duration when a date_end is set
        """
        cleaned_data = self.cleaned_data
        if cleaned_data.get('date_end'):
            if not cleaned_data.get('duration'):
                cleaned_data['duration'] = 0
                del self._errors['duration']
            date_start = cleaned_data.get('date_start', 0)
            date_end = cleaned_data.get('date_end')
            if date_end <= date_start:
                self._errors['date_end'] = self.error_class(
                    {'Should be later than date start'})

        return cleaned_data

    def save(self, commit=True):
        event = self.instance

        # XXX to keep compatibility: should be remove in a next release
        if hasattr(self.instance, 'title'):
            event.title = self.cleaned_data['title_en']
        if hasattr(self.instance, 'summary'):
            event.summary = self.cleaned_data['summary_en']

        create = not event.id
        # XXX to get the save_m2m
        super(EventForm, self).save(commit)
        try:
            if not commit:
                event.save()
            event_data = None
            if create:
                event_data = TranslateEventData()
                event_data.lang = TranslateLang.objects.get(iso='en')
                event_data.user = self.request.user
                event_data.event = event

            elif 'title_en' in self.changed_data or \
                    'summary_en' in self.changed_data:
                event_data = event.eventdatas.get(lang__iso='en')
            if event_data:
                event_data.title = self.cleaned_data['title_en']
                event_data.summary = self.cleaned_data['summary_en']
                event_data.save()
        except Exception as err:
            LOG.error('error when save the EventForm: %s', err)
        return event

    class Meta:
        model = models.Event
        allowed_char = SocialNetworks.get_max_char()
        widgets = {
            'services': CheckboxSelectMultiple(),
            'msg': Textarea(attrs={'cols': math.ceil(allowed_char / 2.0),
                                   'rows': 2,
                                   'maxlength': allowed_char})
        }
        fields = '__all__'


class EventLogForm(ModelForm):
    comment_en = CharField(required=False, widget=Textarea, label='Comment')

    def __init__(self, *args, **kwargs):
        super(EventLogForm, self).__init__(*args, **kwargs)
        self.fields['comment_en'].widget.attrs.update(
            {'class': 'vLargeTextField'})

        if 'instance' in kwargs and kwargs['instance']:
            eventlog = kwargs['instance']
            try:
                eventlog_data = eventlog.eventlogdatas.get(lang__iso='en')
                self.fields['comment_en'].initial = eventlog_data.comment
            except Exception as err:
                LOG.error('error when initializing the EventLogForm: %s', err)
                # XXX to keep compatibility: should be remove in a next release
                self.fields['comment_en'].initial = eventlog.comment

    def save(self, commit=True):
        eventlog = self.instance

        eventlog.user = self.request.user

        # XXX to keep compatibility: should be remove in a next release
        if hasattr(eventlog, 'comment'):
            eventlog.comment = self.cleaned_data['comment_en']

        create = not eventlog.id
        # XXX to get the save_m2m method which might be need in the adminform
        super(EventLogForm, self).save(commit)
        try:
            if not commit:
                eventlog.save()
            eventlog_data = None
            if create:
                eventlog_data = TranslateEventLogData()
                eventlog_data.lang = TranslateLang.objects.get(iso='en')
                eventlog_data.user = self.request.user
                eventlog_data.eventlog = eventlog
            elif 'comment_en' in self.changed_data:
                eventlog_data = eventlog.eventlogdatas.get(lang__iso='en')
            if eventlog_data:
                eventlog_data.comment = self.cleaned_data['comment_en']
                eventlog_data.save()
        except Exception as err:
            LOG.error('error when saving the EventLogForm: %s', err)
        return eventlog

    class Meta:
        model = models.EventLog
        allowed_char = SocialNetworks.get_max_char()
        widgets = {
            'msg': Textarea(attrs={'cols': math.ceil(allowed_char / 2.0),
                                   'rows': 2,
                                   'maxlength': allowed_char})
        }
        fields = '__all__'
