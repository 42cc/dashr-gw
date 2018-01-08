from decimal import Decimal

from django.test import TestCase

from apps.core.models import GatewaySettings
from apps.core.utils import (
    get_minimal_deposit_amount,
    get_minimal_withdrawal_amount,
    get_received_amount,
)


class UtilsTest(TestCase):
    def setUp(self):
        GatewaySettings.objects.create(
            gateway_fee_percent=Decimal('0.5'),
            max_dash_miner_fee=Decimal('0.001'),
        )

    def test_get_received_amount_deposit(self):
        self.assertEqual(
            get_received_amount('1', 'deposit'),
            Decimal('0.995'),
        )
        self.assertEqual(
            get_received_amount('1.1', 'deposit'),
            Decimal('1.0945'),
        )
        self.assertEqual(
            get_received_amount('0', 'deposit'),
            Decimal('0'),
        )
        self.assertEqual(
            get_received_amount('1.123456789', 'deposit'),
            Decimal('1.11783949'),
        )
        self.assertEqual(
            get_received_amount('1.123456784', 'deposit'),
            Decimal('1.11783949'),
        )

    def test_get_received_amount_withdrawal(self):
        self.assertEqual(
            get_received_amount('1', 'withdrawal'),
            Decimal('0.994'),
        )
        self.assertEqual(
            get_received_amount('1.1', 'withdrawal'),
            Decimal('1.0935'),
        )
        self.assertEqual(
            get_received_amount('0', 'withdrawal'),
            Decimal('0'),
        )
        self.assertEqual(
            get_received_amount('1.123456789', 'withdrawal'),
            Decimal('1.11683949'),
        )
        self.assertEqual(
            get_received_amount('1.123456784', 'withdrawal'),
            Decimal('1.11683949'),
        )

    def test_get_minimal_deposit_amount(self):
        self.assertEqual(
            get_minimal_deposit_amount(),
            Decimal('0.00000002'),
        )

    def test_get_minimal_withdrawal_amount(self):
        self.assertEqual(
            get_minimal_withdrawal_amount(),
            Decimal('0.00100504'),
        )
