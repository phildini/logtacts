from django.contrib.auth.models import User
from django.db import models

from contacts.models import Book


class StripeCustomer(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User)
    stripe_id = models.CharField(max_length=255)
    default_source = models.CharField(max_length=255)
    email = models.EmailField(blank=True)


class StripeSubscription(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(StripeCustomer)
    book = models.ForeignKey(Book)
    stripe_id = models.CharField(max_length=255)
    paid_until = models.DateTimeField(blank=True, null=True)
