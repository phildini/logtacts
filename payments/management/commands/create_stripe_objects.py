import logging
import stripe
from django.core.management.base import BaseCommand
from django.utils import timezone

from contacts.models import Book, BookOwner
from payments.models import StripeCustomer, StripeSubscription

logger = logging.getLogger('scripts')

class Command(BaseCommand):
    help = "Create stripe objects for existing ContactOtter obejcts"

    def handle(self, *args, **options):
        for book in Book.objects.filter(customer__isnull=True):
            print(book.name)
            print(book.paid_until)
            try:
                customer = StripeCustomer.objects.get(user=book.owner)
            except StripeCustomer.DoesNotExist:
                customer = StripeCustomer.objects.create_for_user(user=book.owner)
            try:
                sub = StripeSubscription.objects.get(customer=customer, book=book)
            except StripeSubscription.DoesNotExist:
                if book.is_paid():
                    sub = StripeSubscription.objects.create_for_customer(
                        customer=customer,
                        book=book,
                        paid_until=book.paid_until,
                        quantity=len(book.owners()),
                    )
            book.customer = customer
            book.save