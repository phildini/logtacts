from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class ProfileForm(forms.ModelForm):

    send_contact_reminders = forms.BooleanField(required=False)
    send_birthday_reminders = forms.BooleanField(required=False)
    check_twitter_dms = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']


class ReviewUserForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ReviewUserForm, self).__init__(*args, **kwargs)
        queryset = User.objects.filter(is_active=False)
        choices = [
            (
                user.id,
                "{}: registered with {} on {}".format(
                    user.username,
                    user.email,
                    user.date_joined,
                )
            ) for user in queryset
        ]

        self.fields['users'] = forms.MultipleChoiceField(
            required=False,
            choices=choices,
            widget=forms.CheckboxSelectMultiple()
        )
