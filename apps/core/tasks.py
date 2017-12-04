import logging
import socket

import celery
from bitcoinrpc.authproxy import JSONRPCException
from ripple_api.management.transaction_processors import monitor_transactions
from ripple_api.models import Transaction as RippleTransaction
from ripple_api.ripple_api import balance as get_ripple_balance, is_trust_set
from ripple_api.tasks import sign_task, submit_task

from django.conf import settings
from django.db.utils import DatabaseError
from django.utils.timezone import now, timedelta

from apps.core import models, wallet
from gateway import celery_app

logger = logging.getLogger(__file__)


@celery_app.task
def monitor_transactions_task(account):
    monitor_transactions(account)


class CeleryDepositTransactionBaseTask(celery.Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        transaction = models.DepositTransaction.objects.only('id').get(
            id=args[0],
        )
        transaction.state = models.DepositTransactionStates.FAILED
        transaction.save()


celery_deposit_transaction_task = celery_app.task(
    base=CeleryDepositTransactionBaseTask,
    # Retry if the system cannot connect to a Dash or DB server.
    autoretry_for=(socket.error, DatabaseError, JSONRPCException),
    retry_kwargs={
        'max_retries': None,
        'countdown': settings.TRANSACTION_OVERDUE_MINUTES,
    },
)


@celery_deposit_transaction_task
def monitor_dash_to_ripple_transaction(transaction_id):
    logger.info('Deposit {}. Monitoring'.format(transaction_id))
    transaction = models.DepositTransaction.objects.get(id=transaction_id)

    dash_wallet = wallet.DashWallet()
    balance = dash_wallet.get_address_balance(transaction.dash_address)
    logger.info('Deposit {}. Balance {}'.format(transaction_id, balance))

    if balance > 0:
        transaction.state = models.DepositTransactionStates.UNCONFIRMED
        transaction.dash_to_transfer = balance
        transaction.save()
        logger.info('Deposit {}. Became unconfirmed'.format(transaction_id))
        monitor_transaction_confirmations_number.delay(transaction_id)
        return

    # If transaction is overdue.
    if transaction.state_changes.only('datetime').get(
        current_state=models.DepositTransactionStates.INITIATED,
    ).datetime + timedelta(
        settings.TRANSACTION_OVERDUE_MINUTES,
    ) < now():
        transaction.state = models.DepositTransactionStates.OVERDUE
        transaction.save(update_fields=('state',))
        logger.info('Deposit {}. Became overdue')
    else:
        raise monitor_dash_to_ripple_transaction.retry(
            (transaction_id,),
            countdown=60,
            max_retries=settings.TRANSACTION_OVERDUE_MINUTES,
        )


@celery_deposit_transaction_task
def monitor_transaction_confirmations_number(transaction_id):
    logger.info(
        'Deposit {}. Monitoring number of confirmations'.format(
            transaction_id,
        ),
    )
    transaction = models.DepositTransaction.objects.get(id=transaction_id)

    dash_wallet = wallet.DashWallet()
    confirmed_balance = dash_wallet.get_address_balance(
        transaction.dash_address,
        settings.DASHD_MINIMAL_CONFIRMATIONS,
    )

    logger.info(
        'Deposit {}. Confirmed balance - {}'.format(
            transaction_id,
            confirmed_balance,
        ),
    )

    if transaction.dash_to_transfer <= confirmed_balance:
        transaction.state = models.DepositTransactionStates.CONFIRMED
        transaction.save(update_fields=('state',))
        logger.info('Deposit {}. Confirmed'.format(transaction_id))
        send_ripple_transaction.delay(transaction_id)
        return

    raise monitor_transaction_confirmations_number.retry(
        (transaction_id,),
        countdown=60,
        max_retries=60,
    )


@celery_deposit_transaction_task
def send_ripple_transaction(transaction_id):
    logger.info(
        'Deposit {}. Sending Ripple transaction'.format(transaction_id),
    )

    dash_transaction = models.DepositTransaction.objects.get(id=transaction_id)

    minimal_trust_limit = (
        dash_transaction.dash_to_transfer +
        get_ripple_balance(
            dash_transaction.ripple_address,
            settings.RIPPLE_ACCOUNT,
            'DSH',
        )
    )
    if not is_trust_set(
        trusts=dash_transaction.ripple_address,
        peer=settings.RIPPLE_ACCOUNT,
        currency='DSH',
        limit=minimal_trust_limit,
    ):
        logger.info(
            'Deposit {}. Ripple account does not trust '
            '(should trust {})'.format(transaction_id, minimal_trust_limit),
        )
        dash_transaction.state = models.TransactionStates.NO_RIPPLE_TRUST
        dash_transaction.save()
        raise send_ripple_transaction.retry(
            (transaction_id,),
            countdown=5 * 60,
            max_retries=100,
        )

    new_ripple_transaction = RippleTransaction.objects.create(
        account=settings.RIPPLE_ACCOUNT,
        destination=dash_transaction.ripple_address,
        currency='DSH',
        value='{0:f}'.format(dash_transaction.dash_to_transfer),
    )

    sign_task(new_ripple_transaction.pk, settings.RIPPLE_SECRET)
    new_ripple_transaction.refresh_from_db()
    if new_ripple_transaction.status != new_ripple_transaction.PENDING:
        logger.error(
            'Deposit {}. Signing Ripple transaction #{} failed'.format(
                transaction_id,
                new_ripple_transaction.id,
            ),
        )
        dash_transaction.state = models.TransactionStates.FAILED
        dash_transaction.save()
        return

    submit_task(new_ripple_transaction.pk)
    new_ripple_transaction.refresh_from_db()
    if new_ripple_transaction.status != new_ripple_transaction.SUBMITTED:
        logger.error(
            'Deposit {}. Submitting Ripple transaction #{} failed'.format(
                transaction_id,
                new_ripple_transaction.id,
            ),
        )
        dash_transaction.state = models.TransactionStates.FAILED
        dash_transaction.save()
        return

    logger.info(
        'Deposit {}. Processed. Ripple transaction {}'.format(
            transaction_id,
            new_ripple_transaction.hash,
        ),
    )
    dash_transaction.state = models.TransactionStates.PROCESSED
    dash_transaction.outgoing_ripple_transaction_hash = (
        new_ripple_transaction.hash
    )
    dash_transaction.save()
