from apps.core.utils import get_minimal_transaction_amount


def minimal_amounts(request):
    if request.is_ajax():
        return
    return {
        'minimal_deposit_amount': get_minimal_transaction_amount('deposit'),
        'minimal_withdrawal_amount': get_minimal_transaction_amount(
            'withdrawal',
        ),
    }
