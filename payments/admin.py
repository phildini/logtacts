from django.contrib import admin

from .models import (
    StripeCustomer,
    StripeCharge,
    StripeInvoice,
    StripeSubscription,
)

admin.site.register(StripeCharge)
admin.site.register(StripeCustomer)
admin.site.register(StripeInvoice)
admin.site.register(StripeSubscription)