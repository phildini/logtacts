from braces.views import LoginRequiredMixin, StaffuserRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.views.generic import (
    FormView,
    UpdateView,
)
from rest_framework.authtoken.models import Token

from contacts import models as contact_models
from invitations.models import Invitation

from . import forms
from . import models


class ProfileView(LoginRequiredMixin, UpdateView):

    form_class = forms.ProfileForm
    model = User
    template_name = "profile.html"

    def get_object(self, *args, **kwargs):
        self.profile = models.Profile.objects.get(user=self.request.user)
        return self.request.user

    def get_context_data(self, *args, **kwargs):
        context = super(ProfileView, self).get_context_data(*args, **kwargs)
        context['tokens'] = Token.objects.filter(user=self.request.user)
        context['social_accounts'] = self.request.user.socialaccount_set.all()
        context['invitations'] = Invitation.objects.filter(sender=self.request.user)
        context['send_contact_reminders'] = self.profile.send_contact_reminders
        context['send_birthday_reminders'] = self.profile.send_birthday_reminders
        context['check_twitter_dms'] = self.profile.check_twitter_dms
        return context

    def get_success_url(self):
        return reverse('profile')

    def form_valid(self, form):
        response = super(ProfileView, self).form_valid(form)
        self.profile.send_contact_reminders = form.cleaned_data.get(
            'send_contact_reminders'
        )
        self.profile.send_birthday_reminders = form.cleaned_data.get(
            'send_birthday_reminders'
        )
        self.profile.check_twitter_dms = form.cleaned_data.get(
            'check_twitter_dms'
        )
        self.profile.save()

        messages.success(self.request, "Profile saved")

        return response


class ReviewUserView(LoginRequiredMixin, StaffuserRequiredMixin, FormView):
    
    form_class = forms.ReviewUserForm
    template_name = "review_users.html"

    def get_success_url(self):
        return '/admin/'

    def form_valid(self, form):
        users = User.objects.filter(id__in=form.cleaned_data.get('users'))
        for user in users:
            user.is_active = True
            user.save()
            book = contact_models.Book.objects.create(
                name="{}'s Contacts".format(user),
            )
            contact_models.BookOwner.objects.create(book=book, user=user)

        subject = '[ContactOtter] Your account is ready!'
        body = 'Your ContactOtter account is all set and ready to go! Hooray!\nLogin at https://{}/login/'.format(
            Site.objects.get_current().domain
        )
        try:
            message = EmailMessage(
                subject=subject,
                body=body,
                from_email='ContactOtter Accounts <account@contactotter.com>',
                to=['account@contactotter.com'],
                bcc=[user.email for user in users if user.email],
            )
            message.send()
        except:
            logger.exception('Problem sending account active email')

        return super(ReviewUserView, self).form_valid(form)

