# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Service'
        db.create_table(u'backoffice_service', (
            (u'id', self.gf('django.db.models.fields.AutoField')
             (primary_key=True)),
            ('name', self.gf('django.db.models.fields.PositiveSmallIntegerField')(
                unique=True)),
            ('description', self.gf(
                'django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'backoffice', ['Service'])

        # Adding model 'Event'
        db.create_table(u'backoffice_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')
             (primary_key=True)),
            ('date_start', self.gf('django.db.models.fields.DateTimeField')
             (default=datetime.datetime.now)),
            ('date_end', self.gf('django.db.models.fields.DateTimeField')
             (default=None, null=True, blank=True)),
            ('estimate_date_end', self.gf(
                'django.db.models.fields.DateTimeField')()),
            ('duration', self.gf(
                'django.db.models.fields.PositiveIntegerField')()),
            ('title', self.gf('django.db.models.fields.CharField')
             (max_length=50)),
            ('summary', self.gf('django.db.models.fields.TextField')
             (default=None, null=True, blank=True)),
            ('category', self.gf(
                'django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal(u'backoffice', ['Event'])

        # Adding M2M table for field services on 'Event'
        db.create_table(u'backoffice_event_services', (
            ('id', models.AutoField(
                verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(orm[u'backoffice.event'], null=False)),
            ('service', models.ForeignKey(
                orm[u'backoffice.service'], null=False))
        ))
        db.create_unique(
            u'backoffice_event_services', ['event_id', 'service_id'])

        # Adding model 'EventLog'
        db.create_table(u'backoffice_eventlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')
             (primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')
             (default=datetime.datetime.now)),
            ('comment', self.gf('django.db.models.fields.TextField')()),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')
             (related_name='eventlogs', to=orm['backoffice.Event'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')
             (related_name='eventlogs', to=orm['auth.User'])),
        ))
        db.send_create_signal(u'backoffice', ['EventLog'])

        # Adding model 'TimeZoneEnum'
        db.create_table(u'backoffice_timezoneenum', (
            (u'id', self.gf('django.db.models.fields.AutoField')
             (primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')
             (max_length=100)),
        ))
        db.send_create_signal(u'backoffice', ['TimeZoneEnum'])

        # Adding model 'TimeZone'
        db.create_table(u'backoffice_timezone', (
            (u'id', self.gf('django.db.models.fields.AutoField')
             (primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')
             (to=orm['auth.User'], unique=True)),
            ('timezone', self.gf('django.db.models.fields.related.ForeignKey')
             (to=orm['backoffice.TimeZoneEnum'])),
        ))
        db.send_create_signal(u'backoffice', ['TimeZone'])

    def backwards(self, orm):
        # Deleting model 'Service'
        db.delete_table(u'backoffice_service')

        # Deleting model 'Event'
        db.delete_table(u'backoffice_event')

        # Removing M2M table for field services on 'Event'
        db.delete_table('backoffice_event_services')

        # Deleting model 'EventLog'
        db.delete_table(u'backoffice_eventlog')

        # Deleting model 'TimeZoneEnum'
        db.delete_table(u'backoffice_timezoneenum')

        # Deleting model 'TimeZone'
        db.delete_table(u'backoffice_timezone')

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'backoffice.event': {
            'Meta': {'ordering': "['id', 'pk']", 'object_name': 'Event'},
            'category': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'date_end': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'date_start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'estimate_date_end': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'events'", 'symmetrical': 'False', 'to': u"orm['backoffice.Service']"}),
            'summary': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'backoffice.eventlog': {
            'Meta': {'ordering': "['-date']", 'object_name': 'EventLog'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'eventlogs'", 'to': u"orm['backoffice.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'eventlogs'", 'to': u"orm['auth.User']"})
        },
        u'backoffice.service': {
            'Meta': {'object_name': 'Service'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.PositiveSmallIntegerField', [], {'unique': 'True'})
        },
        u'backoffice.timezone': {
            'Meta': {'object_name': 'TimeZone'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timezone': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['backoffice.TimeZoneEnum']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'backoffice.timezoneenum': {
            'Meta': {'object_name': 'TimeZoneEnum'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['backoffice']
