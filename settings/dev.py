from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = secret_settings_dev['databases']

CELERY_BROKER_URL = secret_settings_dev['redis-host']
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
