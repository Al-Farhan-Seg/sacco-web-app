from django.db import models


class CodedModel(models.Model):
    """Abstract base whose rows show a human code such as MEM-007."""

    code_prefix = ""

    class Meta:
        abstract = True

    @property
    def code(self):
        return f"{self.code_prefix}-{self.pk:03d}"

    def __str__(self):
        return self.code
