from django.contrib import messages
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.views.generic import UpdateView

from contacts.views import LoggedInMixin


class ProfileView(LoggedInMixin, UpdateView):

    model = User
    template_name = "profile.html"
    fields = ['username', 'first_name', 'last_name', 'email']

    def get_object(self, *args, **kwargs):
        return self.request.user

    def get_success_url(self):
        return reverse('profile')

    def form_valid(self, form):
        response = super(ProfileView, self).form_valid(form)

        messages.success(self.request, "Profile saved")

        return response

