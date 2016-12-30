import decimal
from django.contrib.auth.models import User
from django.db import models

from contacts.models import Book
import payments as payments_constants

CREATED = 'created'
SUCCEEDED = 'succeeded'
FAILED = 'failed'
STATUSES = (
    (CREATED, CREATED),
    (SUCCEEDED, SUCCEEDED),
    (FAILED, FAILED),
)


class StripeCustomer(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User)
    stripe_id = models.CharField(max_length=255)
    default_source = models.CharField(max_length=255)
    email = models.EmailField(blank=True)

    def __str__(self):
        return "Customer: {}".format(self.user.username)


class StripeSubscription(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(StripeCustomer)
    book = models.ForeignKey(Book)
    stripe_id = models.CharField(max_length=255)
    plan = models.CharField(
        max_length=255,
        choices=payments_constants.PLAN_CHOICES,
        blank=True,
        null=True,
    )
    paid_until = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "Subscription for: {}".format(self.book.name)


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
