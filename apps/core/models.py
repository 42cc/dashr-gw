# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django_fsm import FSMIntegerField

from django.db import models
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


class Transaction(models.Model):
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = FSMIntegerField(default=INITIATED, choices=STATE_CHOICES)

    class Meta:
        abstract = True


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
