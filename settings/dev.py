from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = secret_settings_dev['databases']

CELERY_BROKER_URL = 'redis://localhost:6379'
