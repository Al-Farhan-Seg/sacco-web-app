from django import forms

from .models import Account


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["member", "account_number", "account_type", "opening_balance"]
        labels = {
            "member": "Member",
            "account_number": "Account number",
            "account_type": "Account type",
            "opening_balance": "Opening balance (UGX)",
        }
