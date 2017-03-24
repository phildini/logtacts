import logging
from django.core.management.base import BaseCommand

from contacts.models import Book, BookOwner

logger = logging.getLogger('scripts')

class Command(BaseCommand):
    help = "Make sure every book has an owner"

    def handle(self, *args, **options):
        for book in Book.objects.filter(owner__isnull=True):
            for owner in book.owners().order_by('created'):
                book.owner = owner.user
                book.save()