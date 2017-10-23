# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.db import IntegrityError

from apps.core.models import DepositTransaction, Page, Transaction


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


class DepositModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.transaction = DepositTransaction.objects.create(
            ripple_address='rp2PaYDxVwDvaZVLEQv7bHhoFQEyX1mEx7',
            dash_address='XekiLaxnqpFb2m4NQAEcsKutZcZgcyfo6W',
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
