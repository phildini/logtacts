from django.contrib import admin

from .models import StripeCustomer, StripeSubscription

admin.site.register(StripeCustomer)
admin.site.register(StripeSubscription)