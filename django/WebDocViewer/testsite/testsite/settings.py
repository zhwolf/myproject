# -*- coding: utf-8 -*-

"""
Django settings for testsite project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
import logging
import traceback
import StringIO
import locale
import datetime

DEFAULT_ENCODE =  sys.stdin.encoding if sys.stdin.encoding else locale.getdefaultlocale()[1] if locale.getdefaultlocale()[1]  else sys.getdefaultencoding()

print "DEFAULT_ENCODE:",DEFAULT_ENCODE
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'b+iois77vo!^m)bfc%$@)v%ix$ki%@@j+r$z-)qim)1wmj%!rq'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    ### 第三方库
    'haystack',
    'kombu.transport.django',
    #'djcelery',
    'south',
    ### 本地apps
    'apps.backends.DBEnginee',
    'apps.backends.jinja2',
    'apps.docview',
    'testsite',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    #'django.middleware.csrf.CsrfResponseMiddleware',    
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "shared.utils.sharedContext"
)

SESSION_ENGINE= 'django.contrib.sessions.backends.file'
SESSION_EXPIRE_AT_BROWSER_CLOSE=True

ROOT_URLCONF = 'testsite.urls'

WSGI_APPLICATION = 'testsite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'testdb.sqlite3'),
        'OPTIONS': {
            'timeout': 5,
        }            
    }
}

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'zh-CN'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TEMPLATE_STRING_IF_INVALID=''


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

BOOK_ABSPATH = "books/root"
BOOK_BASE= os.path.join(BASE_DIR, BOOK_ABSPATH)

BOOK_OUTPUT_ABSPATH= "books/output"
BOOK_OUTPUT_BASE= os.path.join(BASE_DIR, BOOK_OUTPUT_ABSPATH)

BOOK_TEMP_ABSPATH = "books/temp"
BOOK_TEMP_BASE= os.path.join(BASE_DIR, BOOK_TEMP_ABSPATH)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)



#####
# haystack search
#####
HAYSTACK_DEFAULT_OPERATOR = 'OR'
HAYSTACK_CONNECTIONS = {  
    'default': {  
        #'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',  
        'ENGINE': 'apps.backends.haystack.whoosh_cn_jieba_backend.WhooshEngine',  
        #'ENGINE': 'apps.backends.haystack.whoosh_cn_yaha_backend.WhooshEngine',  
        'PATH': os.path.join(BASE_DIR, 'books/whoosh_index'),  
    },  
}

logging.basicConfig(
    level = logging.DEBUG,
        format = '%(asctime)s %(levelname)s %(module)s.%(funcName)s Line:%(lineno)d %(message)s',
)


def printError():
    fp = StringIO.StringIO()
    traceback.print_exc(file=fp)
    ret = fp.getvalue()
    logging.error("exception:%s",ret)
    
def local2Unicode(str):
    return unicode(str, DEFAULT_ENCODE)
    
def unicode2local(str):
    return str.encode(DEFAULT_ENCODE)    
    
    
#######
# Celery settings
######    

####
#### rabbitmq
#BROKER_URL = 'amqp://guest:guest@localhost:5672//'
#CELERY_RESULT_BACKEND = 'amqp://guest:guest@localhost:5672//'
#CELERY_TASK_SERIALIZER = 'json'

### django db
CELERYD_CONCURRENCY=1
BROKER_URL = 'django://'
#CELERY_RESULT_BACKEND = 'cache+memcached://127.0.0.1:11211/'
CELERY_RESULT_BACKEND='djcelery.backends.cache:CacheBackend'
#CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend'
CELERY_TASK_SERIALIZER = 'json'

##
##redis
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'


CELERYBEAT_SCHEDULE = {
    "runs-every-30-seconds": {
        "task": "apps.docview.tasks.syncBooks",
        "schedule": datetime.timedelta(seconds=60*60),
        
        #"task": "apps.docview.tasks.test_add",
        #"schedule": datetime.timedelta(seconds=30),
        #"args": (16, 16),
            
        "relative": True,
     },
}   