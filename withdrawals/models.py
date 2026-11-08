from django.core.validators import MinValueValidator
from django.db import models

from core.models import CodedModel
from members.models import Member


class Withdrawal(CodedModel):
    code_prefix = "WDR"

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    date = models.DateField()
