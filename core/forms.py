from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class DateInput(forms.DateInput):
    input_type = "date"
    format = "%Y-%m-%d"

    def __init__(self, attrs=None, format=None):
        super().__init__(attrs, format or self.format)


class SignUpForm(UserCreationForm):
    """Account for someone who works in the back-office: a plain user, never staff."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("first_name", "last_name", "email"):
            self.fields[name].required = True
