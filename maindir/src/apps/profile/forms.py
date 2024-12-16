from django import forms
from django.core.exceptions import ValidationError
import re

from apps.profile.models import Profile
from django.contrib.auth.models import User


class EmailVerifyForm(forms.Form):
    email = forms.EmailField(max_length=30)

    def clean_email(self):
        email = self.cleaned_data.get('email')

        gmail_pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'

        if re.match(gmail_pattern, email):
            raise ValidationError("Use a google authentication")

        return email

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('date_of_birth', 'photo')