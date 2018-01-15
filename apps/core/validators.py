# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError

from ripple_api import utils as ripple_api_utils

from apps.core.utils import (
    get_minimal_withdrawal_amount,
)
from apps.core.wallet import DashWallet


def dash_address_validator(address):
    if not DashWallet().check_address_valid(address):
        raise ValidationError(
            'The Dash address is not valid.',
            code='invalid',
        )


def ripple_address_validator(address):
    """
    Ripple address validator
    """
    if not ripple_api_utils.ripple_address_is_valid(address):
        raise ValidationError(
            'The Ripple address is not valid.',
            code='invalid'
        )


def withdrawal_min_dash_amount_validator(amount):
    min_amount = get_minimal_withdrawal_amount()
    if amount < min_amount:
        raise ValidationError(
            'Ensure this value is greater than or equal to {:f}.'.format(
                min_amount,
            ),
        )
