from django import forms

from .models import Staff


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = [
            "first_name",
            "last_name",
            "gender",
            "position",
            "role",
            "contact",
            "address",
        ]
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
            "gender": "Gender",
            "position": "Position",
            "role": "Role",
            "contact": "Contact",
            "address": "Address",
        }
