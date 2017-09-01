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

from apps.core.wallet import DashWallet, RippleWallet

logging.basicConfig(
    filename=os.path.join(settings.BASE_DIR, 'transaction.log'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__file__)
logger.addHandler(logging.StreamHandler())


def process_transactions():
    with sqlite3.connect(
        os.path.join(settings.BASE_DIR, 'transactions.db'),
    ) as connection:
        cursor = connection.cursor()

        dash_wallet = DashWallet()

        dash2ripple_transactions = cursor.execute(
            'SELECT * FROM dash2ripple WHERE processed="FALSE";',
        )
        for transaction in dash2ripple_transactions:
            balance = dash_wallet.get_address_balance(transaction[2])
            if balance:
                transaction_obj = RippleTransaction.objects.create(
                    account=RippleWallet.RIPPLE_ACCOUNT,
                    destination=transaction[1],
                    currency=RippleWallet.dash_currency_code,
                    value='{0:f}'.format(balance),
                )
                sign_task(transaction_obj.pk)
                submit_task(transaction_obj.pk)
                cursor.execute(
                    '''
                    UPDATE dash2ripple SET processed="TRUE" WHERE id={};
                    '''.format(transaction[0]),
                )
                logger.info(
                    'Processed a Dash to Ripple transaction (id={}). '
                    'Sent {0:f} DSH to {}.'.format(
                        transaction[0],
                        balance,
                        transaction[1],
                    ),
                )
            else:
                logger.info('Found no Dash to Ripple transactions.')

        ripple2dash_transactions = cursor.execute(
            'SELECT * FROM ripple2dash WHERE processed="FALSE";',
        )
        for transaction in ripple2dash_transactions:
            transaction_obj = RippleTransaction.objects.filter(
                destination=settings.RIPPLE_ACCOUNT,
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
                    'Processed a Ripple to Dash transaction (id={})'
                    'Sent {} DASH to {}.'.format(
                        transaction[0],
                        transaction_obj[0].value,
                        transaction[1],
                    ),
                )
            else:
                logger.info('Found no Ripple to Dash transactions.')

if __name__ == '__main__':
    process_transactions()
