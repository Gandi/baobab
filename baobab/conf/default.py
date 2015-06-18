"""
use my local db not the dev one
"""

from os.path import abspath, dirname
import sys

HERE = dirname(abspath(__file__))


if 'test' not in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '%s/default.db' % dirname(HERE),
        }
    }
