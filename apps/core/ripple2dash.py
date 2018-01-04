import logging
import os.path
import sqlite3
import sys
import uuid

sys.path.append('../..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway.settings')

from django.conf import settings

from apps.core.models import RippleWalletCredentials

logging.basicConfig(
    filename=os.path.join(settings.BASE_DIR, 'transaction.log'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__file__)


def create_transaction(dash_address):
    with sqlite3.connect(
        os.path.join(settings.BASE_DIR, 'transactions.db'),
    ) as connection:
        cursor = connection.cursor()

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS ripple2dash (
                id INTEGER PRIMARY KEY,
                dash_address CHAR(35),
                processed BOOL DEFAULT FALSE
            );
            ''',
        )

        cursor.execute(
            '''
            INSERT INTO ripple2dash (dash_address) VALUES("{}");
            '''.format(dash_address),
        )

        connection.commit()

        logger.info(
            'Created a new Ripple to Dash transaction (id={}).'.format(
                cursor.lastrowid,
            ),
        )

    ripple_address = RippleWalletCredentials.get_solo().address

    return ripple_address, cursor.lastrowid


if __name__ == '__main__':
    print create_transaction(sys.argv[1])
