import logging
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.views.generic import (
    FormView,
    UpdateView,
)
from rest_framework.authtoken.models import Token

from contacts import models as contact_models
from invitations.models import Invitation
import payments as payment_constants
from payments import models as payments_models

from . import forms
from . import models


sentry = logging.getLogger('sentry')


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
        context['has_twitter'] = context['social_accounts'].filter(
            provider='twitter',
        )
        context['has_foursquare'] = context['social_accounts'].filter(
            provider='foursquare',
        )
        context['invitations'] = Invitation.objects.filter(sender=self.request.user)
        context['send_contact_reminders'] = self.profile.send_contact_reminders
        context['send_birthday_reminders'] = self.profile.send_birthday_reminders
        context['check_twitter_dms'] = self.profile.check_twitter_dms
        context['check_foursquare'] = self.profile.check_foursquare
        context['phone_number'] = self.profile.phone_number
        try:
            book = self.request.current_book
            context['book'] = book
        except contact_models.Book.DoesNotExist:
            book = None
            sentry.error(
                "Couldn't find book for user",
                exc_info=True,
                extra={'user': self.request.user},
            )
        if book:
            try:
                sub = payments_models.StripeSubscription.objects.get(book=book)
                context['plan'] = payment_constants.PLANS.get(sub.plan)
                context['plan_cost_string'] = "{:.2f}".format(
                    context['plan']['stripe_cost'] / 100
                )
            except payment_constants.models.StripeSubscription.DoesNotExist:
                pass
        context["google_import_state"] = cache.get("{}::google-import".format(self.request.user))


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
        self.profile.check_foursquare = form.cleaned_data.get(
            'check_foursquare'
        )
        self.profile.phone_number = form.cleaned_data.get('phone_number')
        self.profile.save()

        messages.success(self.request, "Profile saved")

        return response
