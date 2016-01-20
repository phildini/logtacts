import logging
from django.core.management.base import BaseCommand

from contacts.models import Contact, LogEntry

logger = logging.getLogger('scripts')

class Command(BaseCommand):
    help = "update contact.last_contact to finish migration"

    def handle(self, *args, **options):
        contacts_to_update = Contact.objects.filter(last_contact__isnull=True)
        for contact in contacts_to_update:
            try:
                latest_log = LogEntry.objects.filter(contact=contact).exclude(kind='edit').latest('created')
            except LogEntry.DoesNotExist:
                latest_log = None
            if latest_log:
                time = latest_log.created
                if latest_log.time:
                    time = latest_log.time
                contact.last_contact = time
                contact.save()