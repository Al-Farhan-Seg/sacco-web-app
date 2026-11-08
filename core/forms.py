from django import forms


class DateInput(forms.DateInput):
    input_type = "date"
    format = "%Y-%m-%d"

    def __init__(self, attrs=None, format=None):
        super().__init__(attrs, format or self.format)
