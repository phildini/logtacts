import json
import logging
import requests
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from contacts.models import (
    BookOwner,
    Contact,
    ContactField,
)

CACHE_TIMEOUT = 86400

logger = logging.getLogger('scripts')
sentry = logging.getLogger('sentry')

class Command(BaseCommand):
    help = "send reminder for contacts to contact"

    def handle(self, *args, **options):
        logger.debug("Starting contact reminder sending")
        last_month = timezone.now() - timedelta(weeks=4)
        books_to_check = BookOwner.objects.all()
        for bookowner in books_to_check:
            user = bookowner.user
            book = bookowner.book
            logger.debug("Starting compilation for {}".format(user))
            try:
                contact = Contact.objects.get_contacts_for_user(
                    user=user, book=book,
                ).filter(
                    Q(last_contact__lte=last_month) | Q(last_contact=None),
                    should_surface=True,
                ).order_by('?')[0]
                cache_key = "{}::{}::random".format(user, book)
                cache.set(cache_key, contact.id, CACHE_TIMEOUT)
            except IndexError:
                pass
