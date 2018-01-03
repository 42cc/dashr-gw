from decimal import Decimal, ROUND_DOWN, ROUND_UP

dash_minimal = Decimal('0.00000001')


def get_minimal_withdrawal_amount():
    gateway_fee = Decimal('0.005')
    miner_fee = Decimal('0.001')
    minimal_amount = (dash_minimal + miner_fee) / (1 - gateway_fee)
    minimal_amount = minimal_amount.quantize(
        dash_minimal,
        rounding=ROUND_UP,
    )
    return minimal_amount


def get_received_amount_dash(amount):
    # Round amount to 8 decimal places.
    amount = Decimal(amount).quantize(
        dash_minimal,
        rounding=ROUND_DOWN,
    )

    gateway_fee = Decimal('0.005')
    miner_fee = Decimal('0.001')

    # Subtract fees.
    received_amount = amount * (1 - gateway_fee) - miner_fee

    # Round received amount to 8 decimal places.
    received_amount = received_amount.quantize(
        dash_minimal,
        rounding=ROUND_DOWN,
    )

    return max(received_amount, 0)
