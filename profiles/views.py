from django.contrib import messages
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.views.generic import UpdateView

from contacts.views import LoggedInMixin
from . import forms
from . import models


class ProfileView(LoggedInMixin, UpdateView):

    form_class = forms.ProfileForm
    model = User
    template_name = "profile.html"

    def get_object(self, *args, **kwargs):
        self.profile = models.Profile.objects.get(user=self.request.user)
        return self.request.user

    def get_context_data(self, *args, **kwargs):
        context = super(ProfileView, self).get_context_data(*args, **kwargs)
        context['send_contact_reminders'] = self.profile.send_contact_reminders
        return context

    def get_success_url(self):
        return reverse('profile')

    def form_valid(self, form):
        response = super(ProfileView, self).form_valid(form)
        self.profile.send_contact_reminders = form.cleaned_data.get(
            'send_contact_reminders'
        )
        self.profile.save()

        messages.success(self.request, "Profile saved")

        return response

