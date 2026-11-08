from django import forms

from .models import Member


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["first_name", "last_name", "contact", "address", "email", "gender"]
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
            "contact": "Contact",
            "address": "Address",
            "email": "Email",
            "gender": "Gender",
        }
