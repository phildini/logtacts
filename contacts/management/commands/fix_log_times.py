import logging
from django.core.management.base import BaseCommand

from contacts.models import Contact, LogEntry

logger = logging.getLogger('scripts')

class Command(BaseCommand):
    help = "update logs to have correct time"

    def handle(self, *args, **options):
        logs_to_update = LogEntry.objects.filter(time__isnull=True)
        for log in logs_to_update:
            log.time = log.created
            log.save()
        logger.info("Log time fix completed, {} logs updated".format(len(logs_to_update)))