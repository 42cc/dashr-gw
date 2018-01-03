from decimal import Decimal

from django.test import TestCase

from apps.core.utils import (
    get_received_amount_dash,
)

class UtilsTest(TestCase):
    def test_get_received_amount(self):
        self.assertEqual(get_received_amount_dash('1'), Decimal('0.994'))
        self.assertEqual(get_received_amount_dash('1.1'), Decimal('1.0935'))
        self.assertEqual(get_received_amount_dash('0'), Decimal('0'))
        self.assertEqual(
            get_received_amount_dash('1.123456789'),
            Decimal('1.11683949'),
        )
        self.assertEqual(
            get_received_amount_dash('1.123456784'),
            Decimal('1.11683949'),
        )
