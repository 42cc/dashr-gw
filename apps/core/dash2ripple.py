import logging
import os.path
import sqlite3
import sys

sys.path.append('../..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway.settings')

from django.conf import settings

from apps.core.wallet import DashWallet

logging.basicConfig(
    filename=os.path.join(settings.BASE_DIR, 'transaction.log'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__file__)


def create_transaction(ripple_address):
    with sqlite3.connect(
        os.path.join(settings.BASE_DIR, 'transactions.db'),
    ) as connection:
        cursor = connection.cursor()

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS dash2ripple (
                id INTEGER PRIMARY KEY,
                ripple_address CHAR(35),
                dash_address CHAR(35),
                processed BOOL DEFAULT FALSE
            );
            ''',
        )

        dash_address = DashWallet().get_new_address()

        cursor.execute(
            '''
            INSERT INTO dash2ripple (ripple_address, dash_address)
            VALUES("{}", "{}");
            '''.format(ripple_address, dash_address),
        )

        connection.commit()

        logger.info(
            'Created a new Dash to Ripple transaction (id={}).'.format(
                cursor.lastrowid,
            ),
        )

    return dash_address


if __name__ == '__main__':
    print create_transaction(sys.argv[1])
