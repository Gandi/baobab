# -*- coding: utf-8 -*-
# Django settings for baobab project.
from os.path import abspath, dirname, isfile, exists
import sys

# to locally override the default conf
import getpass
import imp

DEBUG = True
TEMPLATE_DEBUG = DEBUG
TEST = 'test' in sys.argv
HERE = dirname(abspath(__file__))
ROOT_DIR = HERE
HTML_MINIFY = True

USE_ETAGS = True
INFINITE_CACHE = False
SERVE_GZIP = False

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

# XXX need the trailing /
URL_EVENT = 'http://a.url/timeline/events/'

# twitter info
# TWITTER_CONSUMER_KEY = ""
TWITTER_CONSUMER_SECRET = ""

TWITTER_ACCESS_TOKEN = ""
TWITTER_ACCESS_TOKEN_SECRET = ""

TWITTER_MAX_CHAR = 140
TWITTER_URL_SHORTENER = 22
# XXX -1 for the space between the text and the url
TWITTER_ALLOWED_CHAR = TWITTER_MAX_CHAR - TWITTER_URL_SHORTENER - 1
TWITTER_URL_API = 'https://api.twitter.com/1.1/'

# IRC info
IRC = [
    {
        'nick': 'a_nick',
        'username': 'a_user_name',
        'ircname': 'a_irc_name',
        #'password': "",
        # 'port': 6697,
        # 'ssl': True,
        'server': 'a.server.irc',
        'channels': [
            {'name': '#chan', },
            {'name': '#chan2', 'password': 'pwd_chan2'},
        ],
        'prefix': '-all-',
        'on_welcome': 'Hi everyone',
        'on_quit': 'Going down for maintance will be back soon',
    }
]

IRC_SOCKET_PATH = '/run/baobab/baobab_irc.sock'

# see RFC http://tools.ietf.org/html/rfc2812#page-6
# -2 for the mandatory end '\r\n'
IRC_MAX_CHAR = 512 - 2
# get the longer prefix
LEN = max(map(lambda x: len(x.get('prefix', '')), IRC))
IRC_PREFIX_LEN = LEN + 1 if LEN else 0
# -10 for the id of the event
IRC_URL_LENGTH = len(URL_EVENT) - 10
# XXX -1 for the space between the text and the url
IRC_ALLOWED_CHAR = IRC_MAX_CHAR - IRC_PREFIX_LEN - IRC_URL_LENGTH - 1

# message used by the api
HTTP_NOT_IMPLEMENTED_ERROR = 'Sorry but it\'s not implemented yet\n'  # 501
HTTP_APPLICATION_ERROR = 'Sorry but something went wrong\n'  # 500
HTTP_NOT_FOUND = 'Resource not found\n'  # 404

# API HTML OUTPUT
TITLE_SCHEMA = 'Api schema'
TITLE_RESULT = 'Api result'

if DEBUG:
    # we are in a dev env, you can set a default user
    DEFAULT_USER_LOGIN = 'gandi'
    DEFAULT_USER_PWD = 'gandi'
    DEFAULT_USER_MAIL = 'devnull@gandi.net'

    # PROXY_HOST = ''
    # PROXY_PORT = 8080

MANAGERS = ADMINS

# XXX to avoid error in the prod env with the baoab command you need to localy
#     overwrite the DATABASES in conf/user_name.py
DATABASES = {}

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    }

FIXTURE_DIRS = (
    '%s/fixtures/' % HERE,
)

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.4/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '%s/static/' % HERE

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/static/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# NEEDED FOR THE ADMIN
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    #    'django.contrib.staticfiles.finders.FileSystemFinder',
    #    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'a secret key'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

# 26/03/2015 - remove CommonMiddleware. This fix the issue of no content when
# serving static files.
MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'baobab.middleware.CorsMiddleware',
    #'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'baobab.utils.set_current_timezone.TimezoneMiddleware'
)

ROOT_URLCONF = 'baobab.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'baobab.wsgi.application'

TEMPLATE_DIRS = (
    '',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    # XXX need to be first to be able to path correctly for test
    #     See TestSocialNetwork.test test_10_get_max_char_ko
    'baobab.socialnetwork',
    'baobab.backoffice',
    'baobab.apirest',
    'baobab.front',
    'baobab.translate',
    'baobab.rss',
    'baobab.cron',
)

APPEND_SLASH = False
TASTYPIE_ALLOW_MISSING_SLASH = True
TASTYPIE_DEFAULT_FORMATS = ['json', 'html']
API_LIMIT_PER_PAGE = 0

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

if DEBUG or TEST:
    import warnings
    warnings.filterwarnings(
        'error', r'DateTimeField .* received a naive datetime',
        RuntimeWarning, r'django\.db\.models\.fields')

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'syslog': {
            'format': '%(name)s: [%(process)d] [%(levelname)s] %(message)s',
        },
        'console': {
            'format': '%(asctime)s [%(levelname)s]: %(name)s - %(message)s',
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'syslog': {
            'level': 'INFO',
            'class': 'logging.handlers.SysLogHandler',
            'address': '/dev/log',
            'formatter': 'syslog',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'stream': 'ext://sys.stdout',
            'formatter': 'console',
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': [
            'console',
            'syslog',
        ],
        'propagate': True,
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

if not exists('/dev/log'):
    # disable syslog for travis
    del LOGGING['formatters']['syslog']
    del LOGGING['handlers']['syslog']
    LOGGING['root']['handlers'].remove('syslog')

import mimetypes
mimetypes.add_type("application/vnd.ms-fontobject", ".eot", True)
mimetypes.add_type("application/font-woff", ".woff", True)
mimetypes.add_type("font/ttf", ".ttf", True)
mimetypes.add_type("font/otf", ".otf", True)


# allow override the default conf
conf_file = '%s/conf/%s.py' % (HERE, getpass.getuser())
if not isfile(conf_file) and DEBUG:
    conf_file = '%s/conf/default.py' % HERE

if isfile(conf_file):
    # the purpose here is to 'replace' the default 'baobab.settings' by
    # an other one but still keep it as 'baobab.settings' and
    # not a 'baobab.settings.conf.user_name'

    imp.load_source('baobab.settings', conf_file)
    # for python >= 3.3 do this
    # importlib.machinery.SourceFileLoader('baobab.settings',
    #                                      conf_file).load_module()
