# -*- coding: utf-8 -*-
"""
HACK to apply new migrations to the base fixtures

the base fixtures are the one in settings.FIXTURE_DIRS
the name of the fixtures has to be of the form: db_app_name.json
this means one file by app

a mandatory file: db_migrations.json which keeps track of applied migrations

the global var APP define on which app this hack should be applied
"""

import os
import re
from StringIO import StringIO
import sys

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from baobab.utils.handle_south import HandleSouth


class Command(BaseCommand):
    regex = re.compile(r'^[0-9]{4}.*\.py$')
    fixtures = []

    def write(self, file_, lines):
        if not isinstance(lines, list):
            lines = [lines, ]
        for line in lines:
            file_.write(line.rstrip(' \n'))
            file_.write('\n')

    def migrate(self, app):
        """
        dump the new fixture remove the ending whitespce and add the missing \n
        """

        print 'backup the new fixtures: %s' % app
        backup = sys.stdout
        file_ = open('%s/db_%s.json' % (settings.FIXTURE_DIRS[0], app), 'w')
        sys.stdout = StringIO()
        call_command('dumpdata', app, indent=2)
        sys.stdout.seek(0)
        self.write(file_, sys.stdout.readlines())

        file_.close()
        sys.stdout.close()
        sys.stdout = backup

    def has_fixtures(self, app):
        if not self.fixtures:
            for rep in settings.FIXTURE_DIRS:
                self.fixtures.extend(map(lambda x: x.split('.', 1)[0],
                                         os.listdir(rep)))
        return 'db_%s' % app in self.fixtures

    def handle(self, *args, **options):
        if 'test' not in sys.argv or not settings.FIXTURE_DIRS:
            print 'ERROR: not in test env'
            exit(1)
        HandleSouth.disable()

        call_command('migrate', interactive=False)

        HandleSouth.enable()
        # migration already done
        call_command('loaddata', 'db_migrations', verbosity='0')
        call_command('loaddata', 'db_user', verbosity='0')

        for app in HandleSouth.get_apps():
            if not self.has_fixtures(app):
                continue
            print 'loading fixtures: %s' % app
            call_command('loaddata', 'db_%s' % app, verbosity='0')
            nb = MigrationHistory.objects.filter(app_name=app).count()
            files = os.listdir('%s/%s/migrations' % (settings.ROOT_DIR, app))
            migrations = [migration for migration in files
                          if self.regex.match(migration)]
            migrations.sort()
            for migration in migrations[nb:]:
                # XXX schemamigration will always be done by the syncdb command
                #     they shouldn't be done again: e.g raise table not found
                #     datamigration are 'manually' created unlike
                #     schemamigration so a schemamigration should always
                #     contain '_auto__' in its name
                if '_auto__' in migration:
                    call_command('migrate', app, migration, fake=True)
                else:
                    call_command('migrate', app, migration)
            self.migrate(app)
        # update the done migration
        self.migrate('migrations')
