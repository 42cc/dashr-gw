import decimal
import logging
import os.path
import sqlite3
import sys

from bitcoinrpc.authproxy import JSONRPCException

sys.path.append('../..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway.settings')

import django
from django.conf import settings

django.setup()

from ripple_api.models import Transaction as RippleTransaction
from ripple_api.tasks import sign_task, submit_task

from apps.core.models import RippleWalletCredentials
from apps.core.wallet import DashWallet, RippleWallet

logging.basicConfig(
    filename=os.path.join(settings.BASE_DIR, 'transaction.log'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__file__)
logger.addHandler(logging.StreamHandler())


def process_dash_to_ripple(cursor, dash_wallet):
    dash2ripple_transactions = cursor.execute(
        'SELECT * FROM dash2ripple WHERE processed="FALSE";',
    ).fetchall()
    if not dash2ripple_transactions:
        logger.info('Found no Dash to Ripple transactions.')
    ripple_credentials = RippleWalletCredentials.objects.get()
    for transaction in dash2ripple_transactions:
        balance = dash_wallet.get_address_balance(transaction[2])
        if balance:
            transaction_obj = RippleTransaction.objects.create(
                account=ripple_credentials.address,
                destination=transaction[1],
                currency='DSH',
                value='{0:f}'.format(balance),
            )
            sign_task(transaction_obj.pk, ripple_credentials.secret)
            submit_task(transaction_obj.pk)
            cursor.execute(
                '''
                UPDATE dash2ripple SET processed="TRUE" WHERE id={};
                '''.format(transaction[0]),
            )
            logger.info(
                'Processed a Dash to Ripple transaction (id={}). '
                'Sent {:f} DSH to {}.'.format(
                    transaction[0],
                    balance,
                    transaction[1],
                ),
            )


def process_ripple_to_dash(cursor, dash_wallet):
    ripple2dash_transactions = cursor.execute(
        'SELECT * FROM ripple2dash WHERE processed="FALSE";',
    ).fetchall()
    if not ripple2dash_transactions:
        logger.info('Found no Ripple to Dash transactions.')
        return
    ripple_address = RippleWalletCredentials.objects.only(
        'address',
    ).get().address
    for transaction in ripple2dash_transactions:
        transaction_obj = RippleTransaction.objects.filter(
            destination=ripple_address,
            destination_tag=str(transaction[0]),
        )
        if transaction_obj:
            amount = decimal.Decimal(transaction_obj[0].value)
            try:
                dash_wallet.send_to_address(transaction[1], amount)
            except JSONRPCException as e:
                logger.error(e)
                raise e
            cursor.execute(
                '''
                UPDATE ripple2dash SET processed="TRUE" WHERE id={};
                '''.format(transaction[0]),
            )
            logger.info(
                'Processed a Ripple to Dash transaction (id={}). '
                'Sent {} DASH to {}.'.format(
                    transaction[0],
                    transaction_obj[0].value,
                    transaction[1],
                ),
            )


def process_transactions():
    with sqlite3.connect(
        os.path.join(settings.BASE_DIR, 'transactions.db'),
    ) as connection:
        cursor = connection.cursor()

        dash_wallet = DashWallet()

        if cursor.execute(
            'SELECT COUNT(*) FROM sqlite_master '
            'WHERE type="table" AND name="dash2ripple";',
        ).fetchone()[0]:
            process_dash_to_ripple(cursor, dash_wallet)

        if cursor.execute(
            'SELECT COUNT(*) FROM sqlite_master '
            'WHERE type="table" AND name="ripple2dash";',
        ).fetchone()[0]:
            process_ripple_to_dash(cursor, dash_wallet)


if __name__ == '__main__':
    process_transactions()
