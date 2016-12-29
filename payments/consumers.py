import datetime
import logging
import stripe
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils import timezone

from .models import (
    CREATED,
    SUCCEEDED,
    FAILED,
    StripeCustomer,
    StripeCharge,
    StripeInvoice,
    StripeSubscription,
)


sentry = logging.getLogger('sentry')
logger = logging.getLogger('loggly_logs')


def process_webhook(message):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    event = message.content.get('event')
    data = event.get('data', {}).get('object')
    if not data:
        sentry.error("No data in stripe webhook", exc_info=True, extra={
            'event': event,
        })
        return
    try:
        if event.get('type') == 'invoice.created':
            invoice, created = StripeInvoice.objects.get_or_create(
                stripe_id=data['id'],
                amount=data['amount_due'],
                currency=data['currency'],
            )
            logger.info("Stripe invoice created", extra={
                'stripe_charge': data.get('charge'),
                'stripe_customer': data.get('customer'),
                'stripe_invoice': data.get('id'),
                'invoice_id': invoice.id,
            })
            try:
                customer = StripeCustomer.objects.get(stripe_id=data['customer'])
            except StripeCustomer.DoesNotExist:
                sentry.error(
                    "No StripeCustomer: {}".format(data['customer']),
                    exc_info=True,
                    extra={
                        'event': event,
                    },
                )
                customer = None
            if customer:
                invoice.customer = customer
            for item in data.get('lines', {}).get('data', []):
                subscription = StripeSubscription.objects.get(stripe_id=item['id'])
                invoice.subscriptions.add(subscription)
            invoice.save()
        elif event.get('type') == 'invoice.payment_succeeded':
            invoice, created = StripeInvoice.objects.get_or_create(
                stripe_id=data['id'],
                amount=data['amount_due'],
                currency=data['currency'],
            )
            logger.info("Stripe invoice succeeded", extra={
                'stripe_charge': data.get('charge'),
                'stripe_customer': data.get('customer'),
                'stripe_invoice': data.get('id'),
                'invoice_id': invoice.id,
            })
            invoice.status = SUCCEEDED
            for item in data.get('lines', {}).get('data', []):
                subscription = StripeSubscription.objects.get(stripe_id=item['id'])
                subscription.paid_until = datetime.datetime.fromtimestamp(
                    item['period']['end'],
                )
                subscription.save()
                invoice.subscriptions.add(subscription)
                book = subscription.book
                book.paid_until = datetime.datetime.fromtimestamp(
                    item['period']['end'],
                )
                book.save()
            invoice.save()
            # Receipt sending goes here
        elif event.get('type') == 'invoice.payment_failed':
            invoice, created = StripeInvoice.objects.get_or_create(
                stripe_id=data['id'],
                amount=data['amount_due'],
                currency=data['currency'],
            )
            invoice.status = FAILED
            invoice.save()
            logger.info("Stripe invoice failed", extra={
                'stripe_charge': data.get('charge'),
                'stripe_customer': data.get('customer'),
                'stripe_invoice': data.get('id'),
                'invoice_id': invoice.id,
            })
        elif event.get('type') == 'charge.succeeded':
            try:
                invoice = StripeInvoice.objects.get(stripe_id=data['invoice'])
                invoice_id = invoice.id
            except StripeInvoice.DoesNotExist:
                sentry.error(
                    "No StripeInvoice: {}".format(data['invoice']),
                    exc_info=True,
                    extra={
                        'event': event,
                    },
                )
                invoice = None
                invoice_id = None
            charge, created = StripeCharge.objects.get_or_create(
                stripe_id=data['id'],
                amount=data['amount'],
                currency=data['currency'],
            )
            logger.info("Stripe charge succeeded", extra={
                'stripe_charge': data.get('id'),
                'stripe_customer': data.get('customer'),
                'stripe_invoice': data.get('invoice'),
                'invoice_id': invoice_id,
            })
            if invoice:
                charge.invoice = invoice
            try:
                customer = StripeCustomer.objects.get(stripe_id=data['customer'])
            except StripeCustomer.DoesNotExist:
                sentry.error(
                    "No StripeCustomer: {}".format(data['customer']),
                    exc_info=True,
                    extra={
                        'event': event,
                    },
                )
                customer = None
            if customer:
                charge.customer = customer
            charge.status = SUCCEEDED
            charge.save()
        elif event.get('type') == 'charge.failed':
            try:
                invoice = StripeInvoice.objects.get(stripe_id=data['invoice'])
            except StripeInvoice.DoesNoteExist:
                sentry.error(
                    "No StripeInvoice: {}".format(data['invoice']),
                    exc_info=True,
                    extra={
                        'event': event,
                    },
                )
                invoice = None
            charge, created = StripeCharge.objects.get_or_create(
                stripe_id=data['id'],
                amount=data['amount'],
                currency=data['currency'],
            )
            logger.info("Stripe charge succeeded", extra={
                'stripe_charge': data.get('id'),
                'stripe_customer': data.get('customer'),
                'stripe_invoice': data.get('invoice'),
                'invoice_id': invoice.id,
            })
            if invoice:
                charge.invoice = invoice
            try:
                customer = StripeCustomer.objects.get(stripe_id=data['customer'])
            except StripeCustomer.DoesNotExist:
                sentry.error(
                    "No StripeCustomer: {}".format(data['customer']),
                    exc_info=True,
                    extra={
                        'event': event,
                    },
                )
                customer = None
            if customer:
                charge.customer = customer
            charge.status = FAILED
            charge.save()
        else:
            logger.info("Uncaught Stripe event", exc_info=True, extra={
                'event': event,
            })
    except:
        sentry.error("Error processing stripe webhook", exc_info=True, extra={
            'event': event,
        })
