from django import forms
from django.core.exceptions import ValidationError
import re

class EmailVerifyForm(forms.Form):
    email = forms.EmailField(max_length=30)

    def clean_email(self):
        email = self.cleaned_data.get('email')

        gmail_pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'

        if re.match(gmail_pattern, email):
            raise ValidationError("Use a google authentication")

        return email