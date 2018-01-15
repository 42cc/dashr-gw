# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from encrypted_fields import EncryptedCharField
from mock import patch
from solo.models import SingletonModel

from django.test import TestCase
from django.db import IntegrityError
from django.utils import formats

from apps.core.models import (
    DepositTransaction,
    DepositTransactionStateChange,
    RippleWalletCredentials,
    Page,
    BaseTransaction,
    WithdrawalTransaction,
    WithdrawalTransactionStateChange,
)


class PageModelTest(TestCase):
    """ Tests for page model """

    def test_page_creation_valid(self):
        """ Test successfull page creation """
        count_before = Page.objects.count()
        Page.objects.create(
            slug='test',
            title='test title',
            description='lorem ipsum',
        )
        self.assertEquals(Page.objects.count(), count_before + 1)

    def test_page_creation_invalid(self):
        """ Test page creation with invalid args """
        Page.objects.create(slug='test', title='test page')

        with self.assertRaises(IntegrityError) as context:
            Page.objects.create(slug='test', title='duplicate page')

            error_msg = context.exception.message
            self.assertContains('core_page_slug_key', error_msg)
            self.assertContains(
                'duplicate key value violates unique constraint', error_msg
            )


class BaseTransactionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.transaction = BaseTransaction()

    def test_transaction_model_abstract(self):
        self.assertTrue(self.transaction._meta.abstract)

    def test_has_dash_address(self):
        self.assertTrue(hasattr(self.transaction, 'dash_address'))
        self.assertIsInstance(self.transaction.dash_address, unicode)


class DepositModelTest(TestCase):
    @classmethod
    @patch('apps.core.models.DashWallet.get_new_address')
    def setUpTestData(cls, patched_get_new_address):
        cls.dash_address = 'XekiLaxnqpFb2m4NQAEcsKutZcZgcyfo6W'
        patched_get_new_address.return_value = cls.dash_address
        RippleWalletCredentials.get_solo()
        cls.transaction = DepositTransaction.objects.create(
            ripple_address='rp2PaYDxVwDvaZVLEQv7bHhoFQEyX1mEx7',
            dash_to_transfer=1,
        )

    def test_inherits_base_transaction_model(self):
        self.assertTrue(issubclass(DepositTransaction, BaseTransaction))

    def test_deposit_transaction_has_uuid_primary_key(self):
        self.assertTrue(hasattr(self.transaction, 'id'))
        self.assertIsInstance(self.transaction.id, uuid.UUID)

    def test_has_ripple_address(self):
        self.assertTrue(hasattr(self.transaction, 'ripple_address'))
        self.assertIsInstance(self.transaction.ripple_address, unicode)

    def test_dash_address_is_automatically_set(self):
        self.assertEqual(self.transaction.dash_address, self.dash_address)

    @patch('apps.core.models.DashWallet.get_new_address')
    def test_dash_address_is_not_changed_on_model_save(
        self,
        patched_get_new_address,
    ):
        patched_get_new_address.return_value = (
            'Xv4Wp2HNRzjt41X17ahxT3aFCwRseoGG39'
        )
        self.transaction.save()
        self.assertEqual(self.transaction.dash_address, self.dash_address)
        patched_get_new_address.assert_not_called()

    def test_state_change_instance_is_created_after_save(self):
        last_state_change = DepositTransactionStateChange.objects.last()
        self.assertIsNotNone(last_state_change)
        self.assertEqual(last_state_change.transaction_id, self.transaction.id)
        self.assertEqual(
            last_state_change.current_state,
            self.transaction.get_state_display(),
        )

    def test_get_state_history(self):
        self.transaction.save()
        state_changes = DepositTransactionStateChange.objects.order_by(
            'datetime',
        ).filter(transaction=self.transaction)
        expected_history = [
            {
                'state': state.current_state,
                'timestamp': formats.date_format(
                    state.datetime,
                    'DATETIME_FORMAT',
                ),
            } for state in state_changes
        ]
        self.assertEqual(
            self.transaction.get_state_history(),
            expected_history,
        )


class WithdrawalModelTest(TestCase):
    def test_inherits_base_transaction_model(self):
        self.assertTrue(issubclass(WithdrawalTransaction, BaseTransaction))

    def test_has_destination_tag_property_equal_to_id(self):
        transaction = WithdrawalTransaction()
        self.assertTrue(hasattr(transaction, 'destination_tag'))
        self.assertEqual(transaction.destination_tag, transaction.id)

    def test_get_current_state(self):
        transaction = WithdrawalTransaction.objects.create(
            dash_address='yBVKPLuULvioorP8d1Zu8hpeYE7HzVUtB9',
            dash_to_transfer=1,
        )
        expected_state = transaction.get_state_display().format(
            dash_to_transfer='1',
            ripple_address=RippleWalletCredentials.get_solo().address,
            destination_tag=transaction.destination_tag,
        )
        self.assertEqual(transaction.get_current_state(), expected_state)

    def test_state_change_instance_is_created_after_save(self):
        transaction = WithdrawalTransaction.objects.create(
            dash_address='yBVKPLuULvioorP8d1Zu8hpeYE7HzVUtB9',
            dash_to_transfer=1,
        )
        last_state_change = WithdrawalTransactionStateChange.objects.last()
        self.assertIsNotNone(last_state_change)
        self.assertEqual(last_state_change.transaction_id, transaction.id)
        self.assertEqual(
            last_state_change.current_state,
            transaction.get_current_state(),
        )


class RippleWalletCredentialsModelTest(TestCase):
    def setUp(self):
        RippleWalletCredentials.get_solo()

    def test_is_singelton(self):
        self.assertTrue(issubclass(RippleWalletCredentials, SingletonModel))

    def test_has_address(self):
        self.assertTrue(hasattr(RippleWalletCredentials, 'address'))
        self.assertIsInstance(
            RippleWalletCredentials.get_solo().address,
            unicode,
        )

    def test_has_secret(self):
        self.assertTrue(hasattr(RippleWalletCredentials, 'secret'))
        self.assertIsInstance(
            RippleWalletCredentials.get_solo().secret,
            unicode,
        )
        self.assertIsInstance(
            RippleWalletCredentials._meta.get_field('secret'),
            EncryptedCharField,
        )
