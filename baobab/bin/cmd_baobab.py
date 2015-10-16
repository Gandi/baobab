#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Like the manage.py in django's project with added/overridden command

TODO all 'command' in this file should be move to a real django's command
"""

import os
import sys
import pytz

from django.core.management import execute_from_command_line, call_command
from django.conf import settings

from baobab.utils.handle_south import HandleSouth


def default_user():
    from django.contrib.auth.models import User
    from baobab.backoffice.models import TimeZoneEnum
    argv = sys.argv

    if not User.objects.exists():

        if not TimeZoneEnum.objects.exists():
            print 'Creating the TimeZoneEnum ...'
            for timezone in pytz.common_timezones:
                TimeZoneEnum.objects.create(name=timezone)

        login = getattr(settings, 'DEFAULT_USER_LOGIN', None)
        pwd = getattr(settings, 'DEFAULT_USER_PWD', None)
        mail = getattr(settings, 'DEFAULT_USER_MAIL', None)
        if not mail:
            mail = '%s@gandi.net' % login
        if login and pwd:
            execute_from_command_line([argv[0],
                                       'createsuperuser',
                                       '--username=%s' % login,
                                       '--email=%s' % mail,
                                       '--noinput'])
            user = User.objects.get(username=login)
            user.set_password(pwd)
            user.save()
        else:
            create_user = ''
            while create_user not in ['y', 'n']:
                create_user = raw_input('Do you want to create '
                                        'a user: y/n? ')
                print create_user
            if create_user == 'y':
                execute_from_command_line([argv[0], 'createsuperuser'])


def main():
    argv = sys.argv

    # to set DJANGO_SETTINGS_MODULE which is mandatory to use django
    for idx in range(len(sys.argv)):
        if sys.argv[idx].startswith('--settings'):
            setting = sys.argv.pop(idx)
            if '=' in setting:
                setting = setting.split('=', 1)[1]
            else:
                setting = sys.argv.pop(idx)
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', setting)
            break
    if 'DJANGO_SETTINGS_MODULE' not in os.environ:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baobab.settings')

    # XXX fixe me need the settings to be configure
    from baobab.cron import exec_cron

    if len(argv) < 2:
        execute_from_command_line(argv)
        sys.exit(0)

    if argv[1] == 'syncdb':
        # will create the db, run all migration, add a default user
        execute_from_command_line([argv[0],
                                   'syncdb',
                                   '--migrate',
                                   '--noinput'])
        default_user()
    elif argv[1] == 'setup-dev':
        HandleSouth.disable()
        fixtures = []
        for rep in settings.FIXTURE_DIRS:
            tmp = map(lambda x: x.split('.', 1)[0], os.listdir(rep))
            fixtures.extend(filter(lambda x: x.startswith('db_'), tmp))
            call_command('syncdb', interactive=False)
            default_user()
            print 'loading fixtures ...'
            call_command('loaddata', *fixtures, verbosity=0)
    elif argv[1] == 'test':
        apps = [name.split('.', 1)[1] for name in settings.INSTALLED_APPS
                if name.startswith('baobab.')]
        if not [arg for arg in sys.argv if arg.split('.')[0] in apps]:
            sys.argv.extend(apps)
        execute_from_command_line(sys.argv)
    elif len(argv) > 2 and argv[1] == 'migrate' and argv[2] == 'fixtures':
        sys.argv.append('test')
        execute_from_command_line([argv[0], 'migrate_fixtures'])
    elif not exec_cron(argv[1]):
        execute_from_command_line(argv)


if __name__ == '__main__':
    main()
