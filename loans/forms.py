from django import forms

from core.forms import DateInput

from .models import Loan, LoanPayment


class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ["member", "staff", "loan_amount", "payment_period", "payment_amount"]
        labels = {
            "member": "Member",
            "staff": "Staff",
            "loan_amount": "Loan amount (UGX)",
            "payment_period": "Payment period",
            "payment_amount": "Payment amount (UGX)",
        }


class LoanPaymentForm(forms.ModelForm):
    class Meta:
        model = LoanPayment
        fields = ["loan", "amount", "date"]
        labels = {
            "loan": "Loan",
            "amount": "Amount (UGX)",
            "date": "Date",
        }
        widgets = {"date": DateInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["loan"].queryset = Loan.objects.select_related("member")
