from controllers.transaction import TransactionController
from settings import celery_app


@celery_app.task
def observe_condition(condition_id):
    tc = TransactionController(condition_id)
    tc.run()

    return True
