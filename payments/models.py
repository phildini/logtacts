import decimal
from datetime import timedelta
import stripe
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

import payments as payments_constants

CREATED = 'created'
SUCCEEDED = 'succeeded'
FAILED = 'failed'
STATUSES = (
    (CREATED, CREATED),
    (SUCCEEDED, SUCCEEDED),
    (FAILED, FAILED),
)


class StripeCustomerManager(models.Manager):

    def create_for_user(self, user):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        response = stripe.Customer.create(email=user.email)
        customer = self.create(user=user, email=user.email, stripe_id=response['id'])
        return customer

class StripeCustomer(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User)
    stripe_id = models.CharField(max_length=255)
    default_source = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    has_valid_source = models.BooleanField(default=False)

    objects = StripeCustomerManager()

    def __str__(self):
        return "Customer: {}".format(self.user.username)


class StripeSubscriptionManager(models.Manager):

    def create_for_customer(self, customer, book, trial_period_days=0, quantity=1, paid_until=None):
        if not paid_until and trial_period_days > 0:
            paid_until = timezone.now() + timedelta(days=trial_period_days)
        if paid_until and trial_period_days < 1 and paid_until > timezone.now():
            trial_period_days = (paid_until - timezone.now()).days
        stripe.api_key = settings.STRIPE_SECRET_KEY
        return stripe.Subscription.create(
            trial_period_days=trial_period_days,
            plan='monthly_2017_03',
            customer=customer.stripe_id,
            # quantity=quantity,
        )
        return self.create(
            customer=customer,
            is_active=True,
            paid_until=paid_until,
            book=book,
        )


class StripeSubscription(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(StripeCustomer)
    book = models.ForeignKey("contacts.Book", blank=True, null=True)
    stripe_id = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    plan = models.CharField(
        max_length=255,
        choices=payments_constants.PLAN_CHOICES,
        blank=True,
        null=True,
    )
    paid_until = models.DateTimeField(blank=True, null=True)

    objects = StripeSubscriptionManager()

    def __str__(self):
        return "Subscription for: {}".format(self.customer.user)


class StripeInvoice(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    stripe_id = models.CharField(max_length=255)
    status = models.CharField(
        max_length=100,
        choices=STATUSES,
        default=CREATED,
    )
    amount = models.IntegerField(blank=True, null=True)
    currency = models.CharField(max_length=10, blank=True, null=True)
    customer = models.ForeignKey(StripeCustomer, blank=True, null=True)
    subscriptions = models.ManyToManyField(StripeSubscription)

    def __str__(self):
        return "Invoice on: {}".format(self.customer)

    def plan_tuples(self):
        tuples = []
        for subscription in self.subscriptions.all():
            plan = payments_constants.PLANS.get(subscription.plan)
            if plan:
                tuples.append((plan['name'], plan['usd_cost']))
        return tuples

    def display_amount(self):
        return '{0:.02f}'.format(float(self.amount)/100)


class StripeCharge(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    stripe_id = models.CharField(max_length=255)
    status = models.CharField(
        max_length=100,
        choices=STATUSES,
        default=CREATED,
    )
    amount = models.IntegerField(blank=True, null=True)
    currency = models.CharField(max_length=10, blank=True, null=True)
    customer = models.ForeignKey(StripeCustomer, blank=True, null=True)
    invoice = models.ForeignKey(StripeInvoice, blank=True, null=True)

    def __str__(self):
        return "Charge on: {}".format(self.customer)
