import datetime
import json
import stripe
from braces.views import LoginRequiredMixin
from channels import Channel
from django.conf import settings
from django.contrib import messages

from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
)
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    ListView,
    FormView,
)
from gargoyle import gargoyle

from contacts.models import Book, BookOwner

import payments as payment_constants
from .forms import PaymentForm
from .models import (
    StripeCustomer,
    StripeSubscription,
)


class PaymentView(LoginRequiredMixin, FormView):

    template_name = "pay.html"
    form_class = PaymentForm

    def dispatch(self, request, *args, **kwargs):
        if not gargoyle.is_active('enable_payments', request):
            return HttpResponseRedirect('/pricing')
        self.plan = request.GET.get('plan')
        plan = payment_constants.PLANS[self.plan]
        if not self.plan or not plan['is_active']:
            messages.warning(self.request, "Please select a plan")
            url = reverse("pricing")
            return HttpResponseRedirect(url)
        try:
            self.book = Book.objects.get_for_user(user=self.request.user)
        except Book.DoesNotExist:
            self.book = None
        return super(PaymentView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(PaymentView, self).get_context_data(*args, **kwargs)
        if not self.book or self.book.owner != self.request.user:
            messages.info(
                self.request,
                "Sorry, only the contact book owner can add a subscription. Please contact them, or email help@contactotter.com",
                )
        context['owns_book'] = self.book and self.book.owner == self.request.user
        context['selected_book'] = self.book 
        context['plan'] = payment_constants.PLANS[self.plan]
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        return context

    def form_valid(self, form):
        books = Book.objects.filter(owner=self.request.user)
        book_ids = books.values('id')
        if self.request.POST.get('book') and self.request.POST.get('book') in book_ids:
            # User has submitted a book to pay for
            self.subscribe_book(
                book=books.filter(id=self.request.POST.get('book'))[0],
                plan=self.plan,
                token=form.cleaned_data['stripeToken'],
                email=form.cleaned_data['stripeEmail'],
            )
        elif self.book:
            # Use the book from the URL
            self.subscribe_book(
                book=self.book,
                plan=self.plan,
                token=form.cleaned_data['stripeToken'],
                email=form.cleaned_data['stripeEmail'],
            )
        else:
            # Use the first book we find
            # TODO: If greater than 1, don't assume
            book = books[0]
            self.subscribe_book(
                book=book,
                plan=self.plan,
                token=form.cleaned_data['stripeToken'],
                email=form.cleaned_data['stripeEmail'],
            )
        return super(PaymentView, self).form_valid(form)

    def get_success_url(self):
        return reverse('contacts-list')

    def subscribe_book(self, book, plan, token, email):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        response = stripe.Customer.create(
            source=token,
            plan=payment_constants.PLANS[plan]['stripe_id'],
            email=email,
        )
        paid_until = datetime.datetime.fromtimestamp(
            response.subscriptions.data[0].current_period_end,
        )
        customer = StripeCustomer.objects.create(
            email=response.email,
            stripe_id=response.id,
            default_source=response.default_source,
            user=self.request.user,
        )
        subscription = StripeSubscription.objects.create(
            customer=customer,
            book=book,
            stripe_id=response.subscriptions.data[0].id,
            paid_until=paid_until,
        )
        book.paid_until = paid_until
        book.plan = plan
        book.save()

        messages.success(
            self.request,
            "Thanks for your payment. Your book is now active!",
        )

@csrf_exempt
def stripe_webhook_view(request):
    body_unicode = request.body.decode('utf-8')
    event_json = json.loads(body_unicode)
    message = {
        'id': event_json['id'],
        'event': event_json,
    }
    Channel('process-stripe-webhook').send(message)
    return HttpResponse(status=200)

