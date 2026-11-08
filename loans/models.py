from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum

from core.models import CodedModel
from members.models import Member
from staff.models import Staff


class Loan(CodedModel):
    code_prefix = "LN"

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    loan_amount = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    payment_period = models.CharField(max_length=100)
    payment_amount = models.PositiveBigIntegerField(
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return f"{self.code} · {self.member.full_name}"

    @property
    def total_paid(self):
        return self.payments.aggregate(total=Sum("amount"))["total"] or 0

    @property
    def outstanding(self):
        return self.loan_amount - self.total_paid


class LoanPayment(CodedModel):
    code_prefix = "PAY"

    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="payments")
    amount = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    date = models.DateField()

    def clean(self):
        # A missing loan or amount is already reported as a field error.
        if self.loan_id is None or self.amount is None:
            return
        others = self.loan.payments.exclude(pk=self.pk)
        remaining = self.loan.loan_amount - (
            others.aggregate(total=Sum("amount"))["total"] or 0
        )
        if self.amount > remaining:
            raise ValidationError(
                f"This payment exceeds the outstanding balance of "
                f"UGX {remaining:,} on this loan."
            )
