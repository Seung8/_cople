from __future__ import absolute_import, unicode_literals

import os
from celery import Celery
from django.conf import settings

# if run celery using dynamic DJANGO_SETTINGS_MODULE valriables,
# use this command that "DJANGO_SETTINGS_MODULE='settings.<env>' celery -A settings worker -l info"

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

celery_app = Celery('settings', broker=settings.CELERY_BROKER_URL)
celery_app.autodiscover_tasks()
celery_app.config_from_object('django.conf:settings', namespace='CELERY')


@celery_app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
