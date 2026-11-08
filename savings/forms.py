from django import forms

from core.forms import DateInput

from .models import Saving


class SavingForm(forms.ModelForm):
    class Meta:
        model = Saving
        fields = ["member", "account", "staff", "payment_method", "amount", "date"]
        labels = {
            "member": "Member",
            "account": "Account",
            "staff": "Staff",
            "payment_method": "Payment method",
            "amount": "Amount (UGX)",
            "date": "Date",
        }
        widgets = {"date": DateInput()}
