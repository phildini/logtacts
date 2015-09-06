from django import forms
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from .models import Invitation


class InvitationForm(forms.ModelForm):

    class Meta:
        model = Invitation
        fields = ['email']

    def clean(self):
        try:
            existing_user = User.objects.get(
                email=self.cleaned_data.get('email'),
            )
        except User.DoesNotExist:
            existing_user = None
        if existing_user:
            raise forms.ValidationError('User with email already exists!')
        return self.cleaned_data

    def save(self, *args, **kwargs):
        self.instance.key = get_random_string(32).lower()
        return super(InvitationForm, self).save(*args, **kwargs)
