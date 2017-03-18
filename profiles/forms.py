from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from captcha.fields import ReCaptchaField

from phonenumber_field.formfields import PhoneNumberField

from contacts.models import Book, BookOwner


class ProfileForm(forms.ModelForm):

    send_contact_reminders = forms.BooleanField(required=False)
    send_birthday_reminders = forms.BooleanField(required=False)
    check_twitter_dms = forms.BooleanField(required=False)
    check_foursquare = forms.BooleanField(required=False)
    phone_number = PhoneNumberField(required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']


class ReCaptchaSignupForm(forms.Form):

    captcha = ReCaptchaField()

    def signup(self, request, user):
        try:
            book = BookOwner.objects.get(user=user)
        except BookOwner.DoesNotExist:
            Book.objects.create_for_user(user)

