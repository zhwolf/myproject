"""
Django settings for testsite project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import logging
import traceback
import StringIO

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'b+iois77vo!^m)bfc%$@)v%ix$ki%@@j+r$z-)qim)1wmj%!rq'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.docview',
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

ROOT_URLCONF = 'testsite.urls'

WSGI_APPLICATION = 'testsite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

#TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
BOOK_ABSPATH = "books/root"
BOOK_BASE= os.path.join(BASE_DIR, BOOK_ABSPATH)

BOOK_OUTPUT_ABSPATH= "books/output"
BOOK_OUTPUT_BASE= os.path.join(BASE_DIR, BOOK_OUTPUT_ABSPATH)

BOOK_TEMP_ABSPATH = "books/temp"
BOOK_TEMP_BASE= os.path.join(BASE_DIR, BOOK_TEMP_ABSPATH)

SWFTOOL_BASE= os.path.join(BASE_DIR, "tools/SWFTools")
SWFTOOLS = {
    'font': os.path.join(SWFTOOL_BASE, "font2swf.exe"),
    'gif' : os.path.join(SWFTOOL_BASE, "gif2swf.exe"),
    'gpdf': os.path.join(SWFTOOL_BASE, "gpdf2swf.exe"),
    'jpeg': os.path.join(SWFTOOL_BASE, "jpeg2swf.exe"),
    'jpg': os.path.join(SWFTOOL_BASE, "jpeg2swf.exe"),
    'pdf': os.path.join(SWFTOOL_BASE, "pdf2swf.exe"),
    'png': os.path.join(SWFTOOL_BASE, "png2swf.exe"),
    'wav': os.path.join(SWFTOOL_BASE, "wav2swf.exe"),
}

UNOCONVTOOL= os.path.join(BASE_DIR, "tools/unoconv/unoconv")

logging.basicConfig(
    level = logging.DEBUG,
        format = '%(asctime)s %(levelname)s %(module)s.%(funcName)s Line:%(lineno)d %(message)s',
)

def printError():
    fp = StringIO.StringIO()
    traceback.print_exc(file=fp)
    ret = fp.getvalue()
    logging.error("exception:%s",ret)