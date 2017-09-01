from gateway import celery_app
from ripple_api.management.transaction_processors import monitor_transactions


@celery_app.task
def monitor_transactions_task(account):
    monitor_transactions(account)
