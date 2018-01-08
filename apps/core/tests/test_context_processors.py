from django.test import RequestFactory, TestCase

from apps.core import context_processors
from apps.core.utils import get_minimal_transaction_amount


class ContextProcessorsTest(TestCase):
    def test_minimal_amounts(self):
        request = RequestFactory().get('')
        context = context_processors.minimal_amounts(request)
        self.assertIn('minimal_deposit_amount', context)
        self.assertEqual(
            context['minimal_deposit_amount'],
            get_minimal_transaction_amount('deposit'),
        )
        self.assertIn('minimal_withdrawal_amount', context)
        self.assertEqual(
            context['minimal_withdrawal_amount'],
            get_minimal_transaction_amount('withdrawal'),
        )
        ajax_request = RequestFactory().get(
            '',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertIsNone(context_processors.minimal_amounts(ajax_request))
