# -*- coding: utf-8 -*-
"""
To create a cron you HAVE TO create a function call `cron_name_of_my_cron`
and import it here.
It will be directly available with the following command:
  $ baoaba name_of_my_cron

XXX

    This should not be done like that but use to tools provided by Django:
     - create a module: app_name/management/commands/cron_name.py
     - create a class that sub-class BaseCommand
     - implement the `handle(self, *args, **options)`

    Pros:
     - have option to your command
     - the help command will list it
     - have it's own help

    Cons:
     - None (???)
"""

from .twitter import cron_twitter
from .close_event import cron_close_event


def exec_cron(cron_name):
    cron = globals().get('cron_%s' % cron_name)
    if cron and callable(cron):
        cron()
        return True
    return False
