from django import forms

from core.forms import DateInput

from .models import Withdrawal


class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = Withdrawal
        fields = ["member", "amount", "date"]
        labels = {
            "member": "Member",
            "amount": "Amount (final balance, UGX)",
            "date": "Date",
        }
        widgets = {"date": DateInput()}
