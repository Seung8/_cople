from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = secret_settings_dev['databases']

CELERY_BROKER_URL = secret_settings_dev['redis-host']
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler'
#         }
#     },
#     'loggers': {
#         'django.db.backends': {
#             'handlers': ['console'],
#             'level': 'DEBUG'
#         }
#     }
# }
