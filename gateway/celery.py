from __future__ import absolute_import

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway.settings')

app = Celery('gateway')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'monitor_transactions': {
        'task': 'apps.core.tasks.monitor_transactions_task',
        'schedule': 30.0,
    },
}
