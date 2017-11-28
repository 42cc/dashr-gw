# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django_fsm import FSMIntegerField

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils import formats
from django.utils.translation import ugettext as _

from apps.core.validators import ripple_address_validator
from apps.core.wallet import DashWallet


class Page(models.Model):
    slug = models.SlugField(max_length=300, db_index=True, unique=True)
    title = models.CharField(verbose_name=_("Title"), max_length=200)
    description = models.TextField(verbose_name=_("Description"), blank=True)

    class Meta:
        ordering = ('-title', )

    def __str__(self):
        return self.title


class TransactionStates(object):
    INITIATED = 1
    UNCONFIRMED = 2
    CONFIRMED = 3
    PROCESSED = 4
    OVERDUE = 5
    FAILED = 6


class DepositTransactionStates(TransactionStates):
    STATE_CHOICES = (
        (TransactionStates.INITIATED, 'Initiated'),
        (
            TransactionStates.UNCONFIRMED,
            'Received an incoming transaction (hash - '
            '{incoming_dash_transaction_hash}). Waiting for '
            '{confirmations_number} confirmations',
        ),
        (
            TransactionStates.CONFIRMED,
            'Confirmed the incoming transaction (hash - '
            '{incoming_dash_transaction_hash}). Initiated an outgoing one',
        ),
        (
            TransactionStates.PROCESSED,
            'Transaction is processed. Hash of a Ripple transaction is '
            '{outgoing_ripple_transaction_hash}',
        ),
        (
            TransactionStates.OVERDUE,
            'Received 0 Dash transactions. Transactions to the address '
            '{dash_address} are no longer tracked',
        ),
        (
            TransactionStates.FAILED,
            'Transaction failed. Please contact our support team',
        ),
    )


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = FSMIntegerField(
        default=DepositTransactionStates.INITIATED,
        choices=DepositTransactionStates.STATE_CHOICES,
    )

    class Meta:
        abstract = True

    def get_state_history(self):
        return [
            {
                'state': state.get_current_state_display().format(
                    confirmations_number=settings.DASHD_MINIMAL_CONFIRMATIONS,
                    **self.__dict__
                ),
                'timestamp': formats.date_format(
                    state.datetime,
                    'DATETIME_FORMAT',
                ),
            } for state in self.state_changes.order_by('datetime').all()
        ]


class DepositTransaction(Transaction):
    ripple_address = models.CharField(
        max_length=35,
        validators=[ripple_address_validator],
    )
    dash_address = models.CharField(max_length=35)

    incoming_dash_transaction_hash = models.CharField(
        max_length=64,
        blank=True,
    )
    outgoing_ripple_transaction_hash = models.CharField(
        max_length=64,
        blank=True,
    )

    def __str__(self):
        return 'Deposit {}'.format(self.id)

    def save(self, *args, **kwargs):
        dash_wallet = DashWallet()
        if not self.dash_address:
            self.dash_address = dash_wallet.get_new_address()
        super(DepositTransaction, self).save(*args, **kwargs)

    @staticmethod
    def post_save_signal_handler(instance, **kwargs):
        DepositTransactionStateChange.objects.create(
            transaction=instance,
            current_state=instance.state,
        )


class BaseTransactionStateChange(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class DepositTransactionStateChange(BaseTransactionStateChange):
    transaction = models.ForeignKey(
        DepositTransaction,
        related_name='state_changes',
    )
    current_state = models.PositiveSmallIntegerField(
        choices=DepositTransactionStates.STATE_CHOICES,
    )


post_save.connect(
    DepositTransaction.post_save_signal_handler,
    sender=DepositTransaction,
)
