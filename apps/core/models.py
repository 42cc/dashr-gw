# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django_fsm import FSMIntegerField

from django.db import models
from django.db.models.signals import post_save
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
    IN_PROGRESS = 2
    COMPLETED = 3
    NOT_PROCESSED = 4
    FAILED = 5

    STATE_CHOICES = (
        (INITIATED, 'Initiated'),
        (IN_PROGRESS, 'In progress'),
        (COMPLETED, 'Completed'),
        (NOT_PROCESSED, 'Not processed'),
        (FAILED, 'Failed'),
    )


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = FSMIntegerField(
        default=TransactionStates.INITIATED,
        choices=TransactionStates.STATE_CHOICES,
    )

    class Meta:
        abstract = True

    def get_state_history(self):
        return [
            {
                'state': state.get_current_state_display(),
                'timestamp': state.datetime,
            } for state in self.state_changes.order_by('datetime').all()
        ]


class DepositTransaction(Transaction):
    ripple_address = models.CharField(
        max_length=35,
        validators=[ripple_address_validator],
    )
    dash_address = models.CharField(max_length=35)
    proceeded = models.BooleanField(default=False)

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
    current_state = models.PositiveSmallIntegerField(
        choices=TransactionStates.STATE_CHOICES,
    )

    class Meta:
        abstract = True


class DepositTransactionStateChange(BaseTransactionStateChange):
    transaction = models.ForeignKey(
        DepositTransaction,
        related_name='state_changes',
    )


post_save.connect(
    DepositTransaction.post_save_signal_handler,
    sender=DepositTransaction,
)
