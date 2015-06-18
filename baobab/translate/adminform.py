# -*- coding: utf-8 -*-

"""
Re-define some default admin form
"""
from django.forms import ModelForm

from baobab.translate import models


class EventDataForm(ModelForm):

    def save(self, commit=True):
        if not self.instance:
            self.instance.user = self.request.user
        return super(EventDataForm, self).save(commit)

    class Meta:
        model = models.EventData


class EventLogDataForm(ModelForm):

    def save(self, commit=True):
        if self.instance:
            self.instance.user = self.request.user
        return super(EventLogDataForm, self).save(commit)

    class Meta:
        model = models.EventLogData
