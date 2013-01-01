import os
"""
import datetime, time
print time.strftime('%y%W', datetime.datetime.now().timetuple())
"""
DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEVEL = os.environ.get('SERVER_SOFTWARE', '').startswith('Devel')
ROOT_URLCONF = 'urls'
ADMIN_JID = 'milan.andrejevic@gmail.com'

DATABASE_ENGINE = ''
DATABASE_NAME = ''
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''
"""
import random
sid = '~`!@#$%^&*()_-+=|\{[}]abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
print ''.join(random.sample(sid, 50))
"""
SITE_ID = 1
SECRET_KEY = '5)T\PKrWd}^CB21AsvV9Ox3z!gt6RokXiDc(40eaQ&fG-MF`]$'

TEMPLATE_CONTEXT_PROCESSORS = ('context_processors.auth',
                               'django.core.context_processors.debug',
                               'django.core.context_processors.i18n',)
ROOT_PATH = os.path.dirname(__file__)
TEMPLATE_DIRS = (ROOT_PATH + '/templates', ROOT_PATH,)
MIDDLEWARE_CLASSES = (# 'google.appengine.ext.appstats.recording.AppStatsDjangoMiddleware',
                      'google.appengine.ext.ndb.django_middleware.NdbDjangoMiddleware',
                      'django.middleware.locale.LocaleMiddleware',
                      'django.middleware.common.CommonMiddleware',
                      'django.middleware.http.ConditionalGetMiddleware',
                      'middleware.GoogleAppEngineErrorMiddleware',)
INSTALLED_APPS = ('django.contrib.contenttypes', 'django.contrib.sites',
                  'admin', 'comment', 'entry', 'lib', 'news', 'photo',)

TIMEOUT = 3600 # 1 hour
PER_PAGE = 12
LIMIT = 1024*1024

port = os.environ['SERVER_PORT']
if port and port != '80':
    HOST_NAME = '%s:%s' % (os.environ['SERVER_NAME'], port)
else:
    HOST_NAME = os.environ['SERVER_NAME']

ADMIN_MEDIA_PREFIX = '/static/admin/'
APPEND_SLASH = False
TIME_ZONE = 'Europe/Belgrade'
USE_I18N = True
from fake_i18n import *
