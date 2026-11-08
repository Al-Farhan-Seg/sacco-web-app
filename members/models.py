from django.db import models

from core.models import CodedModel


class Member(CodedModel):
    code_prefix = "MEM"

    GENDER_CHOICES = [("M", "Male"), ("F", "Female")]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    email = models.EmailField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.code} · {self.full_name}"
