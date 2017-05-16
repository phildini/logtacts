import json
import logging
import requests
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db.models import Count
from django.utils import timezone
from contacts.models import (
    Book,
    Contact,
    ContactField,
)

CACHE_TIMEOUT = 86400

logger = logging.getLogger('scripts')
sentry = logging.getLogger('sentry')

class Command(BaseCommand):
    help = "find possible merges, store them in redis"

    def handle(self, *args, **options):
        today = timezone.now()
        for book in Book.objects.filter(paid_until__gt=today):
            cached_data = []
            duplicate_contact_fields = ContactField.objects.filter(
                contact__book_id=book.id
            ).values(
                'value'
            ).annotate(
                Count('id')
            ).order_by().filter(id__count__gt=1)[:5]
            for field in duplicate_contact_fields:
                cached_data.append(
                    Contact.objects.filter(book=book, contactfield__value=field['value']).values_list('id', flat=True)
                )
            cache_key = "{}::merges".format(book.id)
            cache.set(cache_key, cached_data, CACHE_TIMEOUT)
