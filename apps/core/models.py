# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from encrypted_fields import EncryptedCharField
from solo.models import SingletonModel

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils import formats
from django.utils.translation import ugettext as _

from apps.core.validators import (
    dash_address_validator,
    ripple_address_validator,
)
from apps.core.wallet import DashWallet


class RippleWalletCredentials(SingletonModel):
    address = models.CharField(
        max_length=35,
        validators=[ripple_address_validator],
        verbose_name='Address',
    )
    secret = EncryptedCharField(max_length=29, verbose_name='Secret key')

    def __str__(self):
        return 'Ripple Wallet Credentials'

    class Meta:
        verbose_name = 'Ripple Wallet Credentials'


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
    NO_RIPPLE_TRUST = 7


class BaseTransaction(models.Model, TransactionStates):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    dash_address = models.CharField(
        max_length=35,
        validators=[dash_address_validator],
    )
    dash_to_transfer = models.DecimalField(
        max_digits=16,
        decimal_places=8,
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True

    def get_state_history(self):
        return [
            {
                'state': state.current_state,
                'timestamp': formats.date_format(
                    state.datetime,
                    'DATETIME_FORMAT',
                ),
            } for state in self.state_changes.order_by('datetime').all()
        ]


class DepositTransaction(BaseTransaction):
    STATE_CHOICES = (
        (TransactionStates.INITIATED, 'Initiated'),
        (
            TransactionStates.UNCONFIRMED,
            'Received an incoming transaction ({dash_to_transfer} DASH). '
            'Waiting for {confirmations_number} confirmations',
        ),
        (
            TransactionStates.CONFIRMED,
            'Confirmed the incoming transaction ({dash_to_transfer} DASH). '
            'Initiated an outgoing one',
        ),
        (
            TransactionStates.PROCESSED,
            'Transaction is processed. Hash of a Ripple transaction is '
            '{outgoing_ripple_transaction_hash}',
        ),
        (
            TransactionStates.OVERDUE,
            '`Received 0 Dash transactions. Transactions to the address '
            '{dash_address} are no longer tracked',
        ),
        (
            TransactionStates.FAILED,
            'Transaction failed. Please contact our support team',
        ),
        (
            TransactionStates.NO_RIPPLE_TRUST,
            'The ripple account {ripple_address} does not trust our gateway. '
            'Please set a trust line to {gateway_ripple_address}',
        ),
    )

    state = models.PositiveSmallIntegerField(
        default=TransactionStates.INITIATED,
        choices=STATE_CHOICES,
    )
    ripple_address = models.CharField(
        max_length=35,
        validators=[ripple_address_validator],
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
        ripple_address = RippleWalletCredentials.objects.only(
            'address',
        ).get().address
        DepositTransactionStateChange.objects.create(
            transaction=instance,
            current_state=instance.get_state_display().format(
                confirmations_number=settings.DASHD_MINIMAL_CONFIRMATIONS,
                gateway_ripple_address=ripple_address,
                **instance.__dict__
            ),
        )


class WithdrawalTransaction(BaseTransaction):
    state = models.PositiveSmallIntegerField(
        default=TransactionStates.INITIATED,
    )

    incoming_ripple_transaction_hash = models.CharField(
        max_length=64,
        blank=True,
    )
    outgoing_dash_transaction_hash = models.CharField(
        max_length=64,
        blank=True,
    )

    def __str__(self):
        return 'Withdrawal {}'.format(self.id)


class BaseTransactionStateChange(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class DepositTransactionStateChange(BaseTransactionStateChange):
    transaction = models.ForeignKey(
        DepositTransaction,
        related_name='state_changes',
    )
    current_state = models.CharField(max_length=500)


post_save.connect(
    DepositTransaction.post_save_signal_handler,
    sender=DepositTransaction,
)
