import logging
import os.path
import sqlite3
import sys
import uuid

sys.path.append('../..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway.settings')

from django.conf import settings

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
                destination_tag CHAR(36) UNIQUE,
                processed BOOL DEFAULT FALSE
            );
            ''',
        )

        destination_tag = uuid.uuid4()

        cursor.execute(
            '''
            INSERT INTO ripple2dash (dash_address, destination_tag)
            VALUES("{}", "{}");
            '''.format(dash_address, destination_tag),
        )

        connection.commit()

        logger.info(
            'Created a new Ripple to Dash transaction (id={}).'.format(
                cursor.lastrowid,
            ),
        )

    return settings.RIPPLE_ACCOUNT, str(destination_tag)


if __name__ == '__main__':
    print create_transaction(sys.argv[1])
