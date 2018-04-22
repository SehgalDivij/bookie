import os
from djangae.settings_base import *
import sys
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.ERROR)
settings_logger = logging.getLogger(__name__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0n&x*r&2b@w*c#!12ywn&=+duo^0=0vmf1f15l(6zc^a53fvr_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'djangae',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'djangae.contrib.contenttypes',
    'djangae.contrib.security',
    'django.contrib.sessions',
    'background_task',
    'rest_framework',
    'api'
]

from telegram import Bot
from telegram.ext import Dispatcher

MIDDLEWARE = [
    'djangae.contrib.security.middleware.AppEngineSecurityMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bookie.urls'

WSGI_APPLICATION = 'bookie.wsgi.application'

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# No static content - API only application.

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

from djangae.db.backends import appengine

DATABASES = {
    'default': {
        'ENGINE': 'djangae.db.backends.appengine'
    }
}

CACHES = {
    'default': {
        'BACKEND': 'bookie.backends.GaeMemcachedCache',
    }
}

from .logger_config import *

TELEGRAM_TOKEN = '580485936:AAH3ktarjxpjhfoXlGr2_1oA4mxXOUXyk0c'

BOT = Bot(TELEGRAM_TOKEN)
DISPATCHER = Dispatcher(BOT, None, workers=0)

# Setup Bot States.
INPUT_DAY = 0
INPUT_TIME = 1
INPUT_NUM_PEOPLE = 2
INPUT_EMAIL = 3
INPUT_REMARKS = 4
VIEW_HISTORY = 5
LOCATION = 6
SHOW_CONFIRMATION_DIALOG = 7
ACCEPT_CONFIRMATION = 8
CONTACT_RESTAURANT = 9
INPUT_TABLE_NUMBER = 10
NO_TABLES_AVAILABLE = 11
EMAIL_OPTIONS = 12
ANY_REMARKS = 13
# Setup Bot States Over

# OUTGOING EMAIL DETAILS
EMAIL_HOST = 'smtp.sendgrid.net'
# This is no longer needed.
EMAIL_PORT = 587
# This is no longer needed.
EMAIL_HOST_USER = 'apikey'
# SENDGRID API KEY is the same as EMAIL_HOST_PASSWORD
# EMAIL_HOST_PASSWORD is no longer needed.
SENDGRID_API_KEY = EMAIL_HOST_PASSWORD = \
    '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'
FROM_EMAIL = 'noreply@thebistro.com'
CONFIRMATION_SUBJECT = 'The Bistro | Order Confirmation'
