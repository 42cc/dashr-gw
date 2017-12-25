import socket
from datetime import timedelta

from mock import patch

from django.conf import settings
from django.db.utils import OperationalError
from django.test import TestCase

from apps.core import models, tasks
from gateway import celery_app


class CeleryTransactionBaseTaskTest(TestCase):
    def setUp(self):
        models.RippleWalletCredentials.get_solo()

    @patch('apps.core.models.DashWallet.get_new_address')
    def test_task_on_failure_with_deposit(self, patched_get_new_address):
        patched_get_new_address.return_value = (
            'XekiLaxnqpFb2m4NQAEcsKutZcZgcyfo6W'
        )
        transaction = models.DepositTransaction.objects.create(
            ripple_address='rp2PaYDxVwDvaZVLEQv7bHhoFQEyX1mEx7',
        )
        task = tasks.CeleryTransactionBaseTask()
        task.on_failure(None, None, (transaction.id,), None, None)
        transaction.refresh_from_db()
        self.assertEqual(transaction.state, transaction.FAILED)

    def test_task_on_failure_with_withdrawal(self):
        transaction = models.WithdrawalTransaction.objects.create(
            dash_address='yBVKPLuULvioorP8d1Zu8hpeYE7HzVUtB9',
        )
        task = tasks.CeleryTransactionBaseTask()
        task.on_failure(None, None, (transaction.id,), None, None)
        transaction.refresh_from_db()
        self.assertEqual(transaction.state, transaction.FAILED)


class MonitorDashToRippleTransactionTaskTest(TestCase):
    @patch('apps.core.models.DashWallet.get_new_address')
    def setUp(self, patched_get_new_address):
        celery_app.conf.update(CELERY_ALWAYS_EAGER=True)
        models.RippleWalletCredentials.get_solo()
        patched_get_new_address.return_value = (
            'XekiLaxnqpFb2m4NQAEcsKutZcZgcyfo6W'
        )
        self.transaction = models.DepositTransaction.objects.create(
            ripple_address='rp2PaYDxVwDvaZVLEQv7bHhoFQEyX1mEx7',
        )

    @patch('apps.core.tasks.monitor_transaction_confirmations_number.delay')
    @patch('apps.core.models.DashWallet.get_address_balance')
    def test_marks_transaction_as_unconfirmed_if_balance_positive(
        self,
        patched_get_address_balance,
        patched_monitor_confirmations_number_task_delay,
    ):
        patched_get_address_balance.return_value = 1
        tasks.monitor_dash_to_ripple_transaction.apply((self.transaction.id,))
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.state, self.transaction.UNCONFIRMED)

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
        self.transaction.timestamp = (
            self.transaction.timestamp -
            timedelta(settings.TRANSACTION_OVERDUE_MINUTES + 1)
        )
        self.transaction.save()
        tasks.monitor_dash_to_ripple_transaction.apply((self.transaction.id,))
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.state, self.transaction.OVERDUE)

    @patch('apps.core.models.DashWallet.get_address_balance')
    def test_not_marks_transaction_as_overdue_if_time_not_exceeded(
        self,
        patched_get_address_balance,
    ):
        patched_get_address_balance.return_value = 0
        tasks.monitor_dash_to_ripple_transaction.apply((self.transaction.id,))
        self.transaction.refresh_from_db()
        self.assertNotEqual(self.transaction.state, self.transaction.OVERDUE)

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


class MonitorTransactionConfirmationsNumberTaskTest(TestCase):
    @patch('apps.core.models.DashWallet.get_new_address')
    def setUp(self, patched_get_new_address):
        celery_app.conf.update(CELERY_ALWAYS_EAGER=True)
        models.RippleWalletCredentials.get_solo()
        patched_get_new_address.return_value = (
            'XekiLaxnqpFb2m4NQAEcsKutZcZgcyfo6W'
        )
        self.transaction = models.DepositTransaction.objects.create(
            ripple_address='rp2PaYDxVwDvaZVLEQv7bHhoFQEyX1mEx7',
        )

    @patch('apps.core.tasks.send_ripple_transaction.delay')
    @patch('apps.core.models.DashWallet.get_address_balance')
    def test_marks_transaction_as_confirmed_if_confirmed_balance_positive(
        self,
        patched_get_address_balance,
        patched_send_ripple_transaction_task_delay,
    ):
        patched_get_address_balance.return_value = 1
        tasks.monitor_transaction_confirmations_number.apply(
            (self.transaction.id,),
        )
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.state, self.transaction.CONFIRMED)

    @patch('apps.core.tasks.send_ripple_transaction.delay')
    @patch('apps.core.models.DashWallet.get_address_balance')
    def test_launches_send_ripple_transaction_if_confirmed_balance_positive(
        self,
        patched_get_address_balance,
        patched_send_ripple_transaction_task_delay,
    ):
        patched_get_address_balance.return_value = 1
        tasks.monitor_transaction_confirmations_number.apply(
            (self.transaction.id,),
        )
        patched_send_ripple_transaction_task_delay.assert_called_once()

    @patch('apps.core.tasks.monitor_transaction_confirmations_number.retry')
    @patch('apps.core.models.DashWallet.get_address_balance')
    def test_retries_if_confirmed_balance_is_not_positive(
        self,
        patched_get_address_balance,
        patched_retry,
    ):
        self.transaction.dash_to_transfer = 1
        self.transaction.save()
        patched_get_address_balance.return_value = 0
        tasks.monitor_transaction_confirmations_number.apply(
            (self.transaction.id,),
        )
        patched_retry.assert_called_once()


class SendRippleTransactionTaskTest(TestCase):
    @patch('apps.core.models.DashWallet.get_new_address')
    def setUp(self, patched_get_new_address):
        models.RippleWalletCredentials.objects.create(
            address='rp2PaYDxVwDvaZVLEQv7bHhoFQEyX1mEx7',
        )
        celery_app.conf.update(CELERY_ALWAYS_EAGER=True)
        patched_get_new_address.return_value = (
            'XekiLaxnqpFb2m4NQAEcsKutZcZgcyfo6W'
        )
        self.transaction = models.DepositTransaction.objects.create(
            ripple_address='rp2PaYDxVwDvaZVLEQv7bHhoFQEyX1mEx7',
            dash_to_transfer=1,
        )

    @staticmethod
    def set_last_ripple_transaction_status(status):
        last_ripple_transaction = tasks.RippleTransaction.objects.last()
        last_ripple_transaction.status = status
        last_ripple_transaction.save()

    @patch('apps.core.tasks.is_trust_set')
    @patch('apps.core.tasks.get_ripple_balance')
    @patch('apps.core.tasks.submit_task')
    @patch('apps.core.tasks.sign_task')
    def test_sends_ripple_tokens_and_marks_transaction_as_processed(
        self,
        patched_sign_task,
        patched_submit_task,
        patched_get_ripple_balance,
        patched_is_trust_set,
    ):
        patched_get_ripple_balance.return_value = 0
        patched_is_trust_set.return_value = True
        patched_sign_task.side_effect = (
            lambda *args: self.set_last_ripple_transaction_status(
                tasks.RippleTransaction.PENDING,
            )
        )
        patched_submit_task.side_effect = (
            lambda *args: self.set_last_ripple_transaction_status(
                tasks.RippleTransaction.SUBMITTED,
            )
        )

        tasks.send_ripple_transaction.apply((self.transaction.id,))

        patched_sign_task.assert_called_once()
        patched_submit_task.assert_called_once()
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.state, self.transaction.PROCESSED)

    @patch('apps.core.tasks.send_ripple_transaction.retry')
    @patch('apps.core.tasks.is_trust_set')
    @patch('apps.core.tasks.get_ripple_balance')
    def test_retries_if_trust_is_not_set(
        self,
        patched_get_ripple_balance,
        patched_is_trust_set,
        patched_retry,
    ):
        patched_get_ripple_balance.return_value = 0
        patched_is_trust_set.return_value = False
        tasks.send_ripple_transaction.apply((self.transaction.id,))
        patched_retry.assert_called_once()

    @patch('apps.core.tasks.is_trust_set')
    @patch('apps.core.tasks.get_ripple_balance')
    @patch('apps.core.tasks.sign_task')
    def test_marks_transaction_as_failed_if_cannot_sign(
        self,
        patched_sign_task,
        patched_get_ripple_balance,
        patched_is_trust_set,
    ):
        patched_get_ripple_balance.return_value = 0
        patched_is_trust_set.return_value = True
        patched_sign_task.side_effect = (
            lambda *args: self.set_last_ripple_transaction_status(
                tasks.RippleTransaction.FAILURE,
            )
        )
        tasks.send_ripple_transaction.apply((self.transaction.id,))
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.state, self.transaction.FAILED)

    @patch('apps.core.tasks.is_trust_set')
    @patch('apps.core.tasks.get_ripple_balance')
    @patch('apps.core.tasks.submit_task')
    @patch('apps.core.tasks.sign_task')
    def test_marks_transaction_as_failed_if_cannot_submit(
        self,
        patched_sign_task,
        patched_submit_task,
        patched_get_ripple_balance,
        patched_is_trust_set,
    ):
        patched_get_ripple_balance.return_value = 0
        patched_is_trust_set.return_value = True
        patched_sign_task.side_effect = (
            lambda *args: self.set_last_ripple_transaction_status(
                tasks.RippleTransaction.PENDING,
            )
        )
        patched_submit_task.side_effect = (
            lambda *args: self.set_last_ripple_transaction_status(
                tasks.RippleTransaction.FAILURE,
            )
        )
        tasks.send_ripple_transaction.apply((self.transaction.id,))
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.state, self.transaction.FAILED)
