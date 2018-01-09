import logging
import socket

import celery
import six
from bitcoinrpc.authproxy import JSONRPCException
from ripple_api.management.transaction_processors import monitor_transactions
from ripple_api.models import Transaction as RippleTransaction
from ripple_api.ripple_api import balance as get_ripple_balance, is_trust_set
from ripple_api.tasks import sign_task, submit_task

from django.conf import settings
from django.db.models import Sum, DecimalField
from django.db.models.functions import Cast
from django.db.utils import DatabaseError
from django.utils.timezone import now, timedelta

from apps.core import models, utils, wallet
from gateway import celery_app

logger = logging.getLogger(__file__)


@celery_app.task
def monitor_transactions_task():
    ripple_address = models.RippleWalletCredentials.get_solo().address
    monitor_transactions(ripple_address)


class CeleryTransactionBaseTask(celery.Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        transaction_id = args[0]
        if isinstance(transaction_id, six.integer_types):
            transaction_model = models.WithdrawalTransaction
        else:
            transaction_model = models.DepositTransaction
        transaction = transaction_model.objects.only('id').get(
            id=transaction_id,
        )
        transaction.state = transaction.FAILED
        transaction.save()


celery_transaction_task = celery_app.task(
    base=CeleryTransactionBaseTask,
    # Retry if the system cannot connect to a Dash or DB server.
    autoretry_for=(socket.error, DatabaseError, JSONRPCException),
    retry_kwargs={
        'max_retries': None,
        'countdown': 60,
    },
    max_retries=None,
)


@celery_transaction_task
def monitor_dash_to_ripple_transaction(transaction_id):
    logger.info('Deposit {}. Monitoring'.format(transaction_id))
    transaction = models.DepositTransaction.objects.get(id=transaction_id)

    dash_wallet = wallet.DashWallet()
    balance = dash_wallet.get_address_balance(transaction.dash_address, 0)
    logger.info(
        'Deposit {}. Received {} (unconfirmed) of {} DASH'.format(
            transaction_id,
            balance,
            transaction.get_normalized_dash_to_transfer(),
        ),
    )

    if balance >= transaction.dash_to_transfer:
        transaction.state = transaction.UNCONFIRMED
        transaction.save(update_fields=('state',))
        logger.info('Deposit {}. Became unconfirmed'.format(transaction_id))
        monitor_transaction_confirmations_number.delay(transaction_id)
        return

    # If transaction is overdue.
    if transaction.timestamp + timedelta(
        minutes=settings.TRANSACTION_OVERDUE_MINUTES,
    ) < now():
        transaction.state = transaction.OVERDUE
        transaction.save(update_fields=('state',))
        logger.info('Deposit {}. Became overdue'.format(transaction_id))
    else:
        raise monitor_dash_to_ripple_transaction.retry(
            (transaction_id,),
            countdown=60,
        )


@celery_transaction_task
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
        'Deposit {}. Confirmed {} of {} DASH'.format(
            transaction_id,
            confirmed_balance,
            transaction.get_normalized_dash_to_transfer(),
        ),
    )

    if transaction.dash_to_transfer <= confirmed_balance:
        transaction.state = transaction.CONFIRMED
        transaction.save(update_fields=('state',))
        logger.info('Deposit {}. Confirmed'.format(transaction_id))
        send_ripple_transaction.delay(transaction_id)
        return

    raise monitor_transaction_confirmations_number.retry(
        (transaction_id,),
        countdown=60,
        max_retries=60,
    )


@celery_transaction_task
def send_ripple_transaction(transaction_id):
    logger.info(
        'Deposit {}. Sending Ripple transaction'.format(transaction_id),
    )

    dash_transaction = models.DepositTransaction.objects.get(id=transaction_id)

    ripple_credentials = models.RippleWalletCredentials.get_solo()

    minimal_trust_limit = (
        dash_transaction.dash_to_transfer +
        get_ripple_balance(
            dash_transaction.ripple_address,
            ripple_credentials.address,
            'DSH',
        )
    )
    if not is_trust_set(
        trusts=dash_transaction.ripple_address,
        peer=ripple_credentials.address,
        currency='DSH',
        limit=minimal_trust_limit,
    ):
        logger.info(
            'Deposit {}. Ripple account does not trust '
            '(should trust {})'.format(transaction_id, minimal_trust_limit),
        )
        dash_transaction.state = dash_transaction.NO_RIPPLE_TRUST
        dash_transaction.save()
        raise send_ripple_transaction.retry(
            (transaction_id,),
            countdown=5 * 60,
            max_retries=100,
        )

    new_ripple_transaction = RippleTransaction.objects.create(
        account=ripple_credentials.address,
        destination=dash_transaction.ripple_address,
        currency='DSH',
        value='{0:f}'.format(
            utils.get_received_amount(
                dash_transaction.get_normalized_dash_to_transfer(),
                'deposit',
            ),
        ),
    )

    sign_task(new_ripple_transaction.pk, ripple_credentials.secret)
    new_ripple_transaction.refresh_from_db()
    if new_ripple_transaction.status != new_ripple_transaction.PENDING:
        logger.error(
            'Deposit {}. Signing Ripple transaction #{} failed'.format(
                transaction_id,
                new_ripple_transaction.id,
            ),
        )
        dash_transaction.state = dash_transaction.FAILED
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
        dash_transaction.state = dash_transaction.FAILED
        dash_transaction.save()
        return

    logger.info(
        'Deposit {}. Processed. Ripple transaction {}'.format(
            transaction_id,
            new_ripple_transaction.hash,
        ),
    )
    dash_transaction.state = dash_transaction.PROCESSED
    dash_transaction.outgoing_ripple_transaction_hash = (
        new_ripple_transaction.hash
    )
    dash_transaction.save()


@celery_transaction_task
def monitor_ripple_to_dash_transaction(transaction_id):
    logger.info('Withdrawal {}. Monitoring'.format(transaction_id))
    transaction = models.WithdrawalTransaction.objects.get(id=transaction_id)

    ripple_gateway_address = models.RippleWalletCredentials.get_solo().address

    ripple_transactions_balance = RippleTransaction.objects.filter(
        destination_tag=transaction.destination_tag,
        currency='DSH',
        issuer=ripple_gateway_address,
        status=RippleTransaction.RECEIVED,
    ).annotate(
        value_decimal=Cast(
            'value',
            DecimalField(max_digits=182, decimal_places=96),
        ),
    ).aggregate(Sum('value_decimal'))['value_decimal__sum']

    if ripple_transactions_balance is not None:
        ripple_transactions_balance = ripple_transactions_balance.normalize()
        logger.info(
            'Withdrawal {}. Received {} of {} DSH'.format(
                transaction_id,
                ripple_transactions_balance,
                transaction.get_normalized_dash_to_transfer(),
            ),
        )
        if ripple_transactions_balance >= transaction.dash_to_transfer:
            transaction.state = transaction.CONFIRMED
            transaction.save(update_fields=('state',))
            send_dash_transaction.delay(transaction_id)
            return
    else:
        logger.info(
            'Withdrawal {}. No transaction found yet'.format(transaction_id),
        )

    if transaction.timestamp + timedelta(
        minutes=settings.TRANSACTION_OVERDUE_MINUTES,
    ) < now():
        transaction.state = transaction.OVERDUE
        transaction.save(update_fields=('state',))
        logger.info('Withdrawal {}. Became overdue'.format(transaction_id))
    else:
        raise monitor_ripple_to_dash_transaction.retry(
            (transaction_id,),
            countdown=60,
        )


@celery_transaction_task
def send_dash_transaction(transaction_id):
    logger.info(
        'Withdrawal {}. Sending Dash transaction'.format(transaction_id),
    )

    transaction = models.WithdrawalTransaction.objects.get(id=transaction_id)

    dash_wallet = wallet.DashWallet()
    dash_transaction_hash = dash_wallet.send_to_address(
        transaction.dash_address,
        utils.get_received_amount(transaction.dash_to_transfer, 'withdrawal'),
    )

    logger.info(
        'Withdrawal {}. Processed. Dash transaction {}'.format(
            transaction_id,
            dash_transaction_hash,
        ),
    )
    transaction.outgoing_dash_transaction_hash = dash_transaction_hash
    transaction.state = transaction.PROCESSED
    transaction.save()
