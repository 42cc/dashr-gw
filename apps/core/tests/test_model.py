# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from mock import patch

from django.test import TestCase
from django.db import IntegrityError

from apps.core.models import (
    DepositTransaction,
    DepositTransactionStateChange,
    Page,
    Transaction,
    TransactionStates,
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


class TransactionModelTest(TestCase):
    def test_transaction_model_abstract(self):
        self.assertTrue(Transaction._meta.abstract)

    def test_transaction_has_uuid_primary_key(self):
        transaction = Transaction()
        self.assertTrue(hasattr(transaction, 'id'))
        self.assertIsInstance(transaction.id, uuid.UUID)

    def test_has_fsm_state_field(self):
        transaction = Transaction()
        self.assertTrue(hasattr(transaction, 'state'))
        self.assertEqual(transaction.state, TransactionStates.INITIATED)


class DepositModelTest(TestCase):
    @classmethod
    @patch('apps.core.models.DashWallet.get_new_address')
    def setUpTestData(cls, patched_get_new_address):
        cls.dash_address = 'XekiLaxnqpFb2m4NQAEcsKutZcZgcyfo6W'
        patched_get_new_address.return_value = cls.dash_address
        cls.transaction = DepositTransaction.objects.create(
            ripple_address='rp2PaYDxVwDvaZVLEQv7bHhoFQEyX1mEx7',
        )

    def test_inherits_transaction_model(self):
        self.assertTrue(issubclass(DepositTransaction, Transaction))

    def test_has_ripple_address(self):
        self.assertTrue(hasattr(self.transaction, 'ripple_address'))
        self.assertIsInstance(self.transaction.ripple_address, unicode)

    def test_has_dash_address(self):
        self.assertTrue(hasattr(self.transaction, 'dash_address'))
        self.assertIsInstance(self.transaction.dash_address, unicode)

    def test_has_proceeded(self):
        self.assertTrue(hasattr(self.transaction, 'proceeded'))
        self.assertIsInstance(self.transaction.proceeded, bool)

    def test_default_proceeded_is_false(self):
        self.assertFalse(self.transaction.proceeded)

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

    @patch('apps.core.models.DashWallet.get_new_address')
    def test_state_change_instance_is_created_after_save(
        self,
        patched_get_new_address,
    ):
        self.transaction.save()
        last_state_change = DepositTransactionStateChange.objects.last()
        self.assertIsNotNone(last_state_change)
        self.assertEqual(last_state_change.transaction_id, self.transaction.id)
        self.assertEqual(
            last_state_change.current_state,
            self.transaction.state,
        )

    @patch('apps.core.models.DashWallet.get_new_address')
    def test_get_state_history(self, patched_get_new_address):
        self.transaction.save()
        state_changes = DepositTransactionStateChange.objects.order_by(
            'datetime',
        ).filter(transaction=self.transaction)
        expected_history = [
            {
                'state': state.get_current_state_display(),
                'timestamp': state.datetime,
            } for state in state_changes
        ]
        self.assertEqual(
            self.transaction.get_state_history(),
            expected_history,
        )

