from django.db import models
from django.db.models import Sum

from core.models import CodedModel
from members.models import Member


class Account(CodedModel):
    code_prefix = "ACC"

    TYPE_CHOICES = [("Savings", "Savings"), ("Current", "Current")]

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    opening_balance = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f"{self.code} · {self.account_number} ({self.account_type})"

    @property
    def balance(self):
        total = self.savings.aggregate(total=Sum("amount"))["total"] or 0
        return self.opening_balance + total
