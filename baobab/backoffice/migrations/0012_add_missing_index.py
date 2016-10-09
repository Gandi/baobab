# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'EventLog', fields ['date']
        db.create_index(u'backoffice_eventlog', ['date'])

        # Adding index on 'Event', fields ['category']
        db.create_index(u'backoffice_event', ['category'])

        # Adding index on 'Event', fields ['estimate_date_end']
        db.create_index(u'backoffice_event', ['estimate_date_end'])

        # Adding index on 'Event', fields ['date_end']
        db.create_index(u'backoffice_event', ['date_end'])

        # Adding index on 'Event', fields ['date_start']
        db.create_index(u'backoffice_event', ['date_start'])

        # Adding index on 'Event',
        # fields ['date_start', 'date_end', 'category']
        db.create_index(u'backoffice_event',
                        ['date_start', 'date_end', 'category'])

        # Adding index on 'Event', fields ['date_start', 'date_end']
        db.create_index(u'backoffice_event', ['date_start', 'date_end'])

        # Adding index on 'Event',
        # fields ['date_start', 'estimate_date_end', 'date_end']
        db.create_index(u'backoffice_event',
                        ['date_start', 'estimate_date_end', 'date_end'])

    def backwards(self, orm):
        # Removing index on 'Event',
        # fields ['date_start', 'estimate_date_end', 'date_end']
        db.delete_index(u'backoffice_event',
                        ['date_start', 'estimate_date_end', 'date_end'])

        # Removing index on 'Event', fields ['date_start', 'date_end']
        db.delete_index(u'backoffice_event', ['date_start', 'date_end'])

        # Removing index on 'Event',
        # fields ['date_start', 'date_end', 'category']
        db.delete_index(u'backoffice_event',
                        ['date_start', 'date_end', 'category'])

        # Removing index on 'Event', fields ['date_start']
        db.delete_index(u'backoffice_event', ['date_start'])

        # Removing index on 'Event', fields ['date_end']
        db.delete_index(u'backoffice_event', ['date_end'])

        # Removing index on 'Event', fields ['estimate_date_end']
        db.delete_index(u'backoffice_event', ['estimate_date_end'])

        # Removing index on 'Event', fields ['category']
        db.delete_index(u'backoffice_event', ['category'])

        # Removing index on 'EventLog', fields ['date']
        db.delete_index(u'backoffice_eventlog', ['date'])

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [],
                    {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [],
                     {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField',
                            [], {'to': u"orm['auth.Permission']",
                                 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {
                'ordering': ("(u'content_type__app_label', "
                             "u'content_type__model', u'codename')"),
                'unique_together': "((u'content_type', u'codename'),)",
                'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [],
                         {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [],
                             {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [],
                    {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [],
                     {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [],
                            {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [],
                      {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [],
                           {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [],
                       {'to': u"orm['auth.Group']", 'symmetrical': 'False',
                        'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [],
                    {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [],
                          {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [],
                         {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [],
                             {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [],
                           {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [],
                          {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [],
                         {'max_length': '128'}),
            'user_permissions': (
                'django.db.models.fields.related.ManyToManyField', [],
                {'to': u"orm['auth.Permission']", 'symmetrical': 'False',
                 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [],
                         {'unique': 'True', 'max_length': '30'})
        },
        u'backoffice.event': {
            'Meta': {'ordering': "['id', 'pk']", 'object_name': 'Event',
                     'index_together': (
                         "[('date_start', 'date_end'), ('date_start', "
                         "'date_end', 'category'), ('date_start', "
                         "'estimate_date_end', 'date_end')]")},
            'category': ('django.db.models.fields.PositiveSmallIntegerField',
                         [], {'db_index': 'True'}),
            'date_end': ('django.db.models.fields.DateTimeField', [],
                         {'default': 'None', 'null': 'True',
                          'db_index': 'True', 'blank': 'True'}),
            'date_start': ('django.db.models.fields.DateTimeField', [],
                           {'default': 'datetime.datetime.now',
                            'db_index': 'True'}),
            'duration': ('django.db.models.fields.PositiveIntegerField',
                         [], {}),
            'estimate_date_end': ('django.db.models.fields.DateTimeField',
                                  [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [],
                    {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [],
                            {'default': 'datetime.datetime.now',
                             'db_index': 'True'}),
            'msg': ('django.db.models.fields.CharField', [],
                    {'default': 'None', 'max_length': '255', 'null': 'True',
                     'blank': 'True'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [],
                         {'symmetrical': 'False', 'related_name': "'events'",
                          'blank': 'True', 'db_index': 'True',
                          'to': u"orm['backoffice.Service']"}),
            'summary': ('django.db.models.fields.TextField', [],
                        {'default': 'None', 'null': 'True',
                         'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [],
                      {'max_length': '255'})
        },
        u'backoffice.eventlog': {
            'Meta': {'ordering': "['-date']", 'object_name': 'EventLog'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [],
                     {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [],
                      {'related_name': "'eventlogs'",
                       'to': u"orm['backoffice.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [],
                    {'primary_key': 'True'}),
            'msg': ('django.db.models.fields.CharField', [],
                    {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [],
                     {'related_name': "'eventlogs'",
                      'to': u"orm['auth.User']"})
        },
        u'backoffice.service': {
            'Meta': {'object_name': 'Service'},
            'description': ('django.db.models.fields.CharField', [],
                            {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [],
                    {'primary_key': 'True'}),
            'name': ('django.db.models.fields.PositiveSmallIntegerField',
                     [], {'unique': 'True'})
        },
        u'backoffice.timezone': {
            'Meta': {'object_name': 'TimeZone'},
            u'id': ('django.db.models.fields.AutoField', [],
                    {'primary_key': 'True'}),
            'timezone': ('django.db.models.fields.related.ForeignKey', [],
                         {'to': u"orm['backoffice.TimeZoneEnum']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [],
                     {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'backoffice.timezoneenum': {
            'Meta': {'object_name': 'TimeZoneEnum'},
            u'id': ('django.db.models.fields.AutoField', [],
                    {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [],
                     {'max_length': '100'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)",
                     'unique_together': "(('app_label', 'model'),)",
                     'object_name': 'ContentType',
                     'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField',
                          [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField',
                    [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField',
                      [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField',
                     [], {'max_length': '100'})
        }
    }

    complete_apps = ['backoffice']
