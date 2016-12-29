from django.contrib import admin

from .models import (
    StripeCustomer,
    StripeCharge,
    StripeInvoice,
    StripeSubscription,
)

class StripeChargeAdmin(admin.ModelAdmin):
    list_display = [
        'stripe_id',
        'status',
        'amount',
        'currency',
        'customer',
        'created',
        'changed',
    ]

admin.site.register(StripeCharge, StripeChargeAdmin)
admin.site.register(StripeCustomer)
admin.site.register(StripeInvoice)
admin.site.register(StripeSubscription)