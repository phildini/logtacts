import datetime
import logging
import stripe
from django.conf import settings

from .models import (
    CREATED,
    SUCCEEDED,
    FAILED,
    StripeCustomer,
    StripeCharge,
    StripeInvoice,
    StripeSubscription,
)


logger = logging.getLogger('sentry')


def process_webhook(message):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    event = message.content.get('event')
    data = event.get('data', {}).get('object')
    if not data:
        logger.error("No data in stripe webhook", exc_info=True, extra={
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
            try:
                customer = StripeCustomer.objects.get(stripe_id=data['customer'])
            except StripeCustomer.DoesNotExist:
                logger.error(
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
        elif event.get('type') == 'invoice.payment_failed':
            invoice, created = StripeInvoice.objects.get_or_create(
                stripe_id=data['id'],
                amount=data['amount_due'],
                currency=data['currency'],
            )
            invoice.status = FAILED
            invoice.save()
        elif event.get('type') == 'charge.succeeded':
            try:
                invoice = StripeInvoice.objects.get(stripe_id=data['invoice'])
            except StripeInvoice.DoesNoteExist:
                logger.error(
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
            if invoice:
                charge.invoice = invoice
            try:
                customer = StripeCustomer.objects.get(stripe_id=data['customer'])
            except StripeCustomer.DoesNotExist:
                logger.error(
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
                logger.error(
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
            if invoice:
                charge.invoice = invoice
            try:
                customer = StripeCustomer.objects.get(stripe_id=data['customer'])
            except StripeCustomer.DoesNotExist:
                logger.error(
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
        logger.error("Error processing stripe webhook", exc_info=True, extra={
            'event': event,
        })

