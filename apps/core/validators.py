# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError

from ripple_api import utils as ripple_api_utils


def ripple_address_validator(address):
    """
    Ripple address validator
    """
    if not ripple_api_utils.ripple_address_is_valid(address):
        raise ValidationError(
            'The Ripple address is not valid.',
            code='invalid'
        )
