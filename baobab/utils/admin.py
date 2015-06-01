# -*- coding: utf-8 -*-
"""
sub class the django Admin class:
 * to have dynamic columns
 * to set the request in the form, which contain the user
 * remove the delete action if you don't have the delete right
"""

from django.db.utils import OperationalError
from django.contrib.admin import (ModelAdmin as DjangoModelAdmin,
                                  StackedInline as DjangoStackedInline,
                                  TabularInline as DjangoTabularInline)


class ModelAdmin(DjangoModelAdmin):

    """
    sub classes need to define a dict `list_display_dynamic` to have dynamic
    columns with True/False value
     - val_name key is a list of tuple:
      - first elem will be used as the conditional value
      - second elem will be used as the columns name
     - filter: a string to define on which filed the obj should be filtered
     - sub_obj: a string to define a sub object
    """

    def __init__(self, *args, **kargs):
        try:
            cls = self.__class__
            if hasattr(cls, 'list_display_dynamic'):
                val_name = cls.list_display_dynamic['val_name']
                filter_ = cls.list_display_dynamic['filter']
                if cls.list_display_dynamic['sub_obj']:
                    sub_objs = cls.list_display_dynamic['sub_obj'].split('.')
                else:
                    sub_objs = []
                for val, name in val_name:

                    def _columns(self, obj, val=val):
                        for sub_obj in sub_objs:
                            obj = getattr(obj, sub_obj)
                        if obj.filter(**{filter_: val}).exists():
                            return '<b>True</b>'
                        return 'False'
                    _columns.short_description = name
                    _columns.allow_tags = True

                    setattr(cls, name, _columns)
                    cls.list_display.append(name)
        except OperationalError as err:
            if not err.message.startswith('no such table'):
                raise
        super(ModelAdmin, self).__init__(*args, **kargs)

    def get_form(self, request, *args, **kwargs):
        form = super(ModelAdmin, self).get_form(request, *args, **kwargs)
        form.request = request
        return form

    def get_actions(self, request):
        actions = super(ModelAdmin, self).get_actions(request)
        if not self.has_delete_permission(request):
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions


class StackedInline(DjangoStackedInline):

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(DjangoStackedInline, self).get_formset(request,
                                                               obj=obj,
                                                               **kwargs)
        formset.form.request = request
        return formset


class TabularInline(DjangoTabularInline):

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(DjangoTabularInline, self).get_formset(request,
                                                               obj=obj,
                                                               **kwargs)
        formset.form.request = request
        return formset
