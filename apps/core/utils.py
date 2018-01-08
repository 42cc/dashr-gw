from decimal import Decimal, ROUND_DOWN, ROUND_UP

from django.apps import apps

dash_minimal = Decimal('0.00000001')


def get_minimal_deposit_amount():
    gateway_settings = apps.get_model('core', 'GatewaySettings').get_solo()
    gateway_fee = gateway_settings.gateway_fee_percent / 100
    minimal_amount = dash_minimal / (1 - gateway_fee)
    minimal_amount = minimal_amount.quantize(
        dash_minimal,
        rounding=ROUND_UP,
    )
    return minimal_amount


def get_minimal_withdrawal_amount():
    gateway_settings = apps.get_model('core', 'GatewaySettings').get_solo()
    gateway_fee = gateway_settings.gateway_fee_percent / 100
    minimal_amount = (
        (dash_minimal + gateway_settings.max_dash_miner_fee) / (1 - gateway_fee)
    )
    minimal_amount = minimal_amount.quantize(
        dash_minimal,
        rounding=ROUND_UP,
    )
    return minimal_amount


def get_received_amount(amount, transaction_type):
    # Round amount to 8 decimal places.
    amount = Decimal(amount).quantize(
        dash_minimal,
        rounding=ROUND_DOWN,
    )

    gateway_settings = apps.get_model('core', 'GatewaySettings').get_solo()
    gateway_fee = gateway_settings.gateway_fee_percent / 100

    # Subtract fees.
    received_amount = amount * (1 - gateway_fee)
    if transaction_type == 'withdrawal':
        received_amount -= gateway_settings.max_dash_miner_fee

    # Round received amount to 8 decimal places.
    received_amount = received_amount.quantize(
        dash_minimal,
        rounding=ROUND_DOWN,
    )

    return max(received_amount, 0)
