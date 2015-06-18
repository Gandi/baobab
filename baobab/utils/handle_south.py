"""
to easily disable the south migration

this is useful to create a local database
and it's also use by the command:
 $ baobab migrate fixture
"""

from django.conf import settings
from django.utils.datastructures import SortedDict


class HandleSouth(object):

    apps = None

    @classmethod
    def get_apps(cls):
        if not cls.apps:
            app = filter(lambda x: x.startswith('baobab.'),
                         settings.INSTALLED_APPS)
            app = map(lambda x: x.rsplit('.', 1)[1], app)
            ignore = ['ignore'] * len(app)
            cls.apps = SortedDict(zip(app, ignore))
        return cls.apps

    @classmethod
    def disable(cls):
        settings.SOUTH_MIGRATION_MODULES = cls.get_apps()

    @classmethod
    def enable(cls):
        if getattr(settings, 'SOUTH_MIGRATION_MODULES'):
            del settings.SOUTH_MIGRATION_MODULES
