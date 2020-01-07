from django.apps import apps

from controllers.transaction import TransactionController
from settings import celery_app


@celery_app.task
def observe_condition(condition_id):
    model = apps.get_model('transaction', 'OrderCondition')
    condition = model.objects.get(id=condition_id)
    tc = TransactionController(condition)
    tc.run()

    return True
