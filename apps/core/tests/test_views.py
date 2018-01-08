from __future__ import unicode_literals

import json
from decimal import Decimal

from mock import patch

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse
from django.test import TestCase
from django.test.client import Client, RequestFactory

from apps.core.models import (
    DepositTransaction,
    Page,
    RippleWalletCredentials,
    WithdrawalTransaction,
)
from apps.core.views import (
    GetReceivedAmountApiView,
    DepositSubmitApiView,
    WithdrawalSubmitApiView,
    DepositStatusApiView,
    WithdrawalStatusApiView,
)


class GetPageDetailsViewTest(TestCase):
    """ Tests for GetPageDetailsView view """

    def setUp(self):
        self.client = Client()
        self.page = Page.objects.create(title='test', slug='test')

    def test_getting_page_by_slug_valid(self):
        """ Test getting page by valid slug """

        response = self.client.get(
            reverse('page', kwargs={'slug': self.page.slug}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', content)
        self.assertIn('page', content)
        self.assertTrue(content['success'])
        self.assertEqual(content['page']['id'], self.page.pk)
        self.assertEqual(content['page']['slug'], self.page.slug)
        self.assertEqual(content['page']['title'], self.page.title)

    def test_getting_page_by_slug_invalid(self):
        """ Test getting page by invalid slug """

        response = self.client.get(
            reverse('page', kwargs={'slug': 'invalid'}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', content)
        self.assertIn('page', content)
        self.assertIn('message', content)
        self.assertFalse(content['success'])
        self.assertEqual(content['message'], 'Page does not exists')
        self.assertEqual(len(content['page']), 0)

    def test_get_page_non_ajax(self):
        """ Test getting page by valid slug """

        response = self.client.get(
            reverse('page', kwargs={'slug': self.page.slug}), follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')


class DepositSubmitApiViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def setUp(self):
        RippleWalletCredentials.get_solo()

    @patch('apps.core.views.monitor_dash_to_ripple_transaction.apply_async')
    @patch('apps.core.models.DashWallet.get_new_address')
    def test_view_with_valid_form(
            self,
            patched_get_new_address,
            patched_monitor_task,
    ):
        patched_get_new_address.return_value = ''
        request = self.factory.post(
            '',
            {
                'ripple_address': 'rp2PaYDxVwDvaZVLEQv7bHhoFQEyX1mEx7',
                'dash_to_transfer': 1,
            },
        )
        response = DepositSubmitApiView.as_view()(request)
        patched_monitor_task.assert_called_once()
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        response_content = json.loads(response.content)
        self.assertIn('success', response_content)
        self.assertIn('dash_wallet', response_content)
        self.assertIn('status_url', response_content)
        self.assertEqual(response_content['success'], True)

    def test_view_with_invalid_form(self):
        request = self.factory.post('', {'ripple_address': 'Invalid address'})
        response = DepositSubmitApiView.as_view()(request)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        response_content = json.loads(response.content)
        self.assertIn('success', response_content)
        self.assertIn('ripple_address_error', response_content)
        self.assertEqual(response_content['success'], False)
        self.assertEqual(
            response_content['ripple_address_error'],
            'The Ripple address is not valid.',
        )


class WithdrawalSubmitApiViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def setUp(self):
        RippleWalletCredentials.get_solo()

    @patch('apps.core.views.monitor_ripple_to_dash_transaction.apply_async')
    @patch('apps.core.models.DashWallet.check_address_valid')
    def test_view_with_valid_form(
        self,
        patched_check_address_valid,
        patched_monitor_task,
    ):
        patched_check_address_valid.return_value = True
        request = self.factory.post(
            '',
            {
                'dash_address': 'yBVKPLuULvioorP8d1Zu8hpeYE7HzVUtB9',
                'dash_to_transfer': 1,
            },
        )
        response = WithdrawalSubmitApiView.as_view()(request)
        patched_monitor_task.assert_called_once()
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        response_content = json.loads(response.content)
        self.assertIn('success', response_content)
        self.assertIn('ripple_address', response_content)
        self.assertIn('destination_tag', response_content)
        self.assertIn('dash_to_transfer', response_content)
        self.assertIn('status_url', response_content)
        self.assertEqual(response_content['success'], True)

    @patch('apps.core.models.DashWallet.check_address_valid')
    def test_view_with_invalid_form(self, patched_check_address_valid):
        patched_check_address_valid.return_value = False
        request = self.factory.post('', {'dash_address': 'Invalid address'})
        response = WithdrawalSubmitApiView.as_view()(request)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        response_content = json.loads(response.content)
        self.assertIn('success', response_content)
        self.assertIn('form_errors', response_content)
        self.assertEqual(response_content['success'], False)
        self.assertEqual(
            response_content['form_errors'],
            {
                'dash_address': ['The Dash address is not valid.'],
                'dash_to_transfer': ['This field is required.'],
            },
        )


class DepositStatusApiViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    @patch('apps.core.models.DashWallet.get_new_address')
    def test_view_returns_valid_data(self, patched_get_new_address):
        patched_get_new_address.return_value = (
            'XekiLaxnqpFb2m4NQAEcsKutZcZgcyfo6W'
        )
        ripple_address = RippleWalletCredentials.get_solo().address
        transaction = DepositTransaction.objects.create(
            ripple_address='rp2PaYDxVwDvaZVLEQv7bHhoFQEyX1mEx7',
            dash_to_transfer=1,
        )
        transaction.state = transaction.UNCONFIRMED
        transaction.save()
        transaction.refresh_from_db()
        request = self.factory.get('')
        response = DepositStatusApiView.as_view()(request, transaction.id)
        expected_response_content = json.dumps(
            {
                'transactionId': transaction.id,
                'state': transaction.get_state_display().format(
                    confirmations_number=settings.DASHD_MINIMAL_CONFIRMATIONS,
                    gateway_ripple_address=ripple_address,
                    **transaction.__dict__
                ),
                'stateHistory': transaction.get_state_history(),
            },
            cls=DjangoJSONEncoder,
        )
        self.assertEqual(response.content, expected_response_content)


class WithdrawalStatusApiViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def test_view_returns_valid_data(self):
        transaction = WithdrawalTransaction.objects.create(
            dash_address='yBVKPLuULvioorP8d1Zu8hpeYE7HzVUtB9',
            dash_to_transfer=1,
        )
        transaction.state = transaction.CONFIRMED
        transaction.save()
        transaction.refresh_from_db()
        request = self.factory.get('')
        response = WithdrawalStatusApiView.as_view()(request, transaction.id)
        expected_response_content = json.dumps(
            {
                'transactionId': transaction.id,
                'state': transaction.get_current_state(),
                'stateHistory': transaction.get_state_history(),
            },
            cls=DjangoJSONEncoder,
        )
        self.assertEqual(response.content, expected_response_content)


class GetReceivedAmountApiViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def test_view_returns_400_without_amount(self):
        request = self.factory.get('')
        response = GetReceivedAmountApiView.as_view()(request)
        self.assertEqual(response.status_code, 400)

    def test_view_returns_400_without_transaction_type(self):
        request = self.factory.get('', {'transaction_type': 'deposit'})
        response = GetReceivedAmountApiView.as_view()(request)
        self.assertEqual(response.status_code, 400)

    def test_view_returns_400_with_invalid_transaction_type(self):
        request = self.factory.get('', {'transaction_type': 'undefined'})
        response = GetReceivedAmountApiView.as_view()(request)
        self.assertEqual(response.status_code, 400)

    def test_view_returns_400_with_invalid_amount(self):
        request = self.factory.get('', {'amount': '9.9.9'})
        response = GetReceivedAmountApiView.as_view()(request)
        self.assertEqual(response.status_code, 400)

    @patch('apps.core.views.get_received_amount')
    def test_view_with_amount(self, patched_get_received_amount):
        patched_get_received_amount.return_value = Decimal(99)
        for transaction_type in ('deposit', 'withdrawal'):
            request = self.factory.get(
                '',
                {'amount': 1, 'transaction_type': transaction_type},
            )
            response = GetReceivedAmountApiView.as_view()(request)
            patched_get_received_amount.assert_called_with(
                '1',
                transaction_type,
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, '{"received_amount": "99"}')
