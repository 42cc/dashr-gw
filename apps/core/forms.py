from django import forms

from apps.core.models import DepositTransaction, WithdrawalTransaction


class DepositTransactionModelForm(forms.ModelForm):
    class Meta:
        model = DepositTransaction
        fields = ('ripple_address',)


class WithdrawalTransactionModelForm(forms.ModelForm):
    class Meta:
        model = WithdrawalTransaction
        fields = ('dash_address', 'dash_to_transfer')
