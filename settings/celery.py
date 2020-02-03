from __future__ import absolute_import, unicode_literals

import os
from celery import Celery
from celery.task import periodic_task
from django.conf import settings

# if run celery using dynamic DJANGO_SETTINGS_MODULE valriables,
# use this command that "DJANGO_SETTINGS_MODULE='settings.<env>' celery -A settings worker -l info -B"

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

celery_app = Celery('settings', broker=settings.CELERY_BROKER_URL)
celery_app.autodiscover_tasks()
celery_app.config_from_object('django.conf:settings', namespace='CELERY')


@celery_app.task
def test(arg):
    """Celery 동작 테스트"""
    print(arg)


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Celery Beat 스케즁 작업 설정"""
    # every 5 seconds
    sender.add_periodic_task(
        5.0, test.s('### celery beat is running!'), name='every_5_seconds'
    )
