from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from accounts.models import Account
from core.models import CodedModel
from members.models import Member
from staff.models import Staff


class Saving(CodedModel):
    code_prefix = "SAV"

    METHOD_CHOICES = [
        ("Cash", "Cash"),
        ("Mobile", "Mobile Money"),
        ("Bank", "Bank Transfer"),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="savings"
    )
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    amount = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    date = models.DateField()

    def clean(self):
        # A missing member or account is already reported as a field error.
        if self.member_id is None or self.account_id is None:
            return
        if self.account.member_id != self.member_id:
            raise ValidationError(
                "This account does not belong to the selected member."
            )
