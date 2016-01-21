from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class ProfileForm(forms.ModelForm):

    send_contact_reminders = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']