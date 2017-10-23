# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext as _


class Page(models.Model):
    slug = models.SlugField(max_length=300, db_index=True, unique=True)
    title = models.CharField(verbose_name=_("Title"), max_length=200)
    description = models.TextField(verbose_name=_("Description"), blank=True)

    class Meta:
        ordering = ('-title', )

    def __str__(self):
        return self.title


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class DepositTransaction(Transaction):
    ripple_address = models.CharField(
        max_length=35,
        validators=[
            RegexValidator(
                '^'
                'r'
                '[rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz]'
                '{27,35}'
                '$',
                message='The Ripple address is not valid.'
            ),
        ],
    )
    dash_address = models.CharField(max_length=35)
    proceeded = models.BooleanField(default=False)

    def __str__(self):
        return 'Deposit {}'.format(self.id)
