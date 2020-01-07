from .base import *

DEBUG = False
ALLOWED_HOSTS = ['*']

DATABASES = secret_settings_prod['databases']

CELERY_BROKER_URL = ''
