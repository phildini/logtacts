import logging
from braces.views import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib import messages
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.views.generic import (
    FormView,
    UpdateView,
)

from contacts.models import Book, BookOwner
from invitations.models import Invitation
import payments as payment_constants
from payments.models import StripeSubscription

from contacts.forms import BookSettingsForm
from contacts.views import BookOwnerMixin

sentry = logging.getLogger('sentry')

class BookSettingsView(BookOwnerMixin, UpdateView):

    form_class = BookSettingsForm
    model = BookOwner
    template_name = "book_settings.html"

    def get_object(self, *args, **kwargs):
        return BookOwner.objects.get(user=self.request.user, book=self.request.current_book)

    def get_context_data(self, *args, **kwargs):
        context = super(BookSettingsView, self).get_context_data(*args, **kwargs)
        context['invitations'] = Invitation.objects.filter(book=self.request.current_book)
        context['book'] = self.request.current_book
        try:
            sub = StripeSubscription.objects.get(book=self.request.current_book)
            context['plan'] = payment_constants.PLANS.get(sub.plan)
            context['plan_cost_string'] = "{:.2f}".format(
                context['plan']['stripe_cost'] / 100
            )
        except StripeSubscription.DoesNotExist:
            pass
        context['google_import_state'] = cache.get("{}::google-import".format(self.request.user))

        return context

    def get_success_url(self):
        return reverse('book_settings', kwargs={'book': self.request.current_book.id})

    def form_valid(self, form):
        response = super(BookSettingsView, self).form_valid(form)
        self.request.current_book.name = form.cleaned_data.get('book_name')
        self.request.current_book.save()

        messages.success(self.request, "Saved!")

        return response

