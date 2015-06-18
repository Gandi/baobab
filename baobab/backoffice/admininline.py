# -*- coding: utf-8 -*-

"""
all the inline class
"""

from baobab.utils.admin import TabularInline
from baobab.backoffice import models
from baobab.backoffice.adminform import EventLogForm


class EventLogInline(TabularInline):

    """
    Used by EventAdmin
    """

    fields = ['comment_en', 'msg']
    model = models.EventLog
    extra = 1
    form = EventLogForm
    ordering = ['date', ]
