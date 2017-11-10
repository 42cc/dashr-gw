from django import forms

from apps.core.models import DepositTransaction


class DepositTransactionModelForm(forms.ModelForm):
    class Meta:
        model = DepositTransaction
        fields = ('ripple_address',)
