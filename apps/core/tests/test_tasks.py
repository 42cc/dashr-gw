import socket
from datetime import timedelta

from mock import patch

from django.conf import settings
from django.db.utils import OperationalError
from django.test import TestCase

from apps.core import models, tasks
from gateway import celery_app


class CeleryDepositTransactionTaskTest(TestCase):
    @patch('apps.core.models.DashWallet.get_new_address')
    def test_task_on_failure(self, patched_get_new_address):
        patched_get_new_address.return_value = (
            'XekiLaxnqpFb2m4NQAEcsKutZcZgcyfo6W'
        )
        transaction = models.DepositTransaction.objects.create(
            ripple_address='rp2PaYDxVwDvaZVLEQv7bHhoFQEyX1mEx7',
        )
        task = tasks.CeleryDepositTransactionTask()
        task.on_failure(None, None, (transaction.id,), None, None)
        transaction.refresh_from_db()
        self.assertEqual(
            transaction.state,
            models.DepositTransactionStates.FAILED,
        )


class MonitorDashToRippleTransactionTaskTest(TestCase):
    @patch('apps.core.models.DashWallet.get_new_address')
    def setUp(self, patched_get_new_address):
        celery_app.conf.update(CELERY_ALWAYS_EAGER=True)
        patched_get_new_address.return_value = (
            'XekiLaxnqpFb2m4NQAEcsKutZcZgcyfo6W'
        )
        self.transaction = models.DepositTransaction.objects.create(
            ripple_address='rp2PaYDxVwDvaZVLEQv7bHhoFQEyX1mEx7',
        )

    @patch('apps.core.models.DashWallet.get_address_balance')
    def test_marks_transaction_as_unconfirmed_if_balance_positive(
        self,
        patched_get_address_balance,
    ):
        patched_get_address_balance.return_value = 1
        tasks.monitor_dash_to_ripple_transaction.apply((self.transaction.id,))
        self.transaction.refresh_from_db()
        self.assertEqual(
            self.transaction.state,
            models.DepositTransactionStates.UNCONFIRMED,
        )

    @patch('apps.core.tasks.monitor_transaction_confirmations_number.delay')
    @patch('apps.core.models.DashWallet.get_address_balance')
    def test_launches_monitoring_confirmations_number_if_balance_positive(
        self,
        patched_get_address_balance,
        patched_monitor_confirmations_number_task_delay,
    ):
        patched_get_address_balance.return_value = 1
        tasks.monitor_dash_to_ripple_transaction.apply((self.transaction.id,))
        patched_monitor_confirmations_number_task_delay.assert_called_once()

    @patch('apps.core.models.DashWallet.get_address_balance')
    def test_marks_transaction_as_overdue_if_time_exceeded(
        self,
        patched_get_address_balance,
    ):
        patched_get_address_balance.return_value = 0
        initial_state = self.transaction.state_changes.get(
            current_state=models.DepositTransactionStates.INITIATED,
        )
        initial_state.datetime = (
            initial_state.datetime -
            timedelta(settings.TRANSACTION_OVERDUE_MINUTES + 1)
        )
        initial_state.save()
        tasks.monitor_dash_to_ripple_transaction.apply((self.transaction.id,))
        self.transaction.refresh_from_db()
        self.assertEqual(
            self.transaction.state,
            models.DepositTransactionStates.OVERDUE,
        )

    @patch('apps.core.models.DashWallet.get_address_balance')
    def test_makes_transaction_as_overdue_if_time_not_exceeded(
        self,
        patched_get_address_balance,
    ):
        patched_get_address_balance.return_value = 0
        tasks.monitor_dash_to_ripple_transaction.apply((self.transaction.id,))
        self.transaction.refresh_from_db()
        self.assertNotEqual(
            self.transaction.state,
            models.DepositTransactionStates.OVERDUE,
        )

    @patch('apps.core.tasks.monitor_dash_to_ripple_transaction.retry')
    @patch('apps.core.models.DashWallet.get_address_balance')
    def test_retries_if_balance_is_not_positive(
        self,
        patched_get_address_balance,
        patched_retry,
    ):
        patched_get_address_balance.return_value = 0
        tasks.monitor_dash_to_ripple_transaction.apply((self.transaction.id,))
        patched_retry.assert_called_once()

    @patch('apps.core.models.DashWallet')
    @patch('apps.core.tasks.monitor_dash_to_ripple_transaction.retry')
    @patch('apps.core.models.DashWallet.get_address_balance')
    def test_retries_if_cannot_connect_to_db(
        self,
        patched_get_address_balance,
        patched_retry,
        patched_model,
    ):
        patched_get_address_balance.return_value = 0
        patched_model.objects.get.side_effect = OperationalError
        tasks.monitor_dash_to_ripple_transaction.apply((self.transaction.id,))
        patched_retry.assert_called_once()

    @patch('apps.core.tasks.monitor_dash_to_ripple_transaction.retry')
    @patch('apps.core.models.DashWallet.get_address_balance')
    def test_retries_if_cannot_connect_to_dash_server(
        self,
        patched_get_address_balance,
        patched_retry,
    ):
        patched_get_address_balance.side_effect = socket.error
        tasks.monitor_dash_to_ripple_transaction.apply((self.transaction.id,))
        patched_retry.assert_called_once()
