from django.db import models

from core.models import CodedModel


class Staff(CodedModel):
    code_prefix = "STF"

    GENDER_CHOICES = [("M", "Male"), ("F", "Female")]
    ROLE_CHOICES = [("Admin", "Admin"), ("User", "User")]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    position = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    contact = models.CharField(max_length=20)
    address = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "staff"

    def __str__(self):
        return f"{self.code} · {self.first_name} {self.last_name}"
