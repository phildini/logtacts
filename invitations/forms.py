from django import forms
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from channels import Channel

from .models import Invitation


class InvitationForm(forms.ModelForm):

    share_book = forms.BooleanField(required=False)

    class Meta:
        model = Invitation
        fields = ['email']

    def clean(self):
        if User.objects.filter(email=self.cleaned_data.get('email')).exists():
            raise forms.ValidationError('User with email already exists!')
        if Invitation.objects.filter(email=self.cleaned_data.get('email')).exists():
            raise forms.ValidationError('User with email already exists!')
        return self.cleaned_data

    def save(self, *args, **kwargs):
        self.instance.key = get_random_string(32).lower()
        response = super(InvitationForm, self).save(*args, **kwargs)
        notification = {
            'id': self.instance.id,
            'created': self.instance.created.strftime("%a %d %b %Y %H:%M"),
        }
        Channel('send-invite').send(notification)
        return response


class InvitationAdminAddForm(forms.ModelForm):

    class Meta:
        model = Invitation
        fields = ['email', 'book', 'sender', 'status']

    def save(self, *args, **kwargs):
        self.instance.key = get_random_string(32).lower()
        response = super(InvitationForm, self).save(*args, **kwargs)
        notification = {
            'id': self.instance.id,
            'created': self.instance.created.strftime("%a %d %b %Y %H:%M"),
        }
        Channel('send-invite').send(notification)
        return super(InvitationAdminAddForm, self).save(*args, **kwargs)


class InvitationAdminUpdateForm(forms.ModelForm):

    class Meta:
        model = Invitation
        fields = '__all__'
