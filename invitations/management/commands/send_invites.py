import logging
import requests
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.utils import timezone

from invitations.consumers import send_invite
from invitations.models import Invitation

logger = logging.getLogger('scripts')

class Command(BaseCommand):
    help = "send invites"

    def handle(self, *args, **options):
        invites_to_send = list(Invitation.objects.filter(
            status=Invitation.PENDING
        ))

        # Grab a few erroring emails each run for a retry.
        invites_to_send += Invitation.objects.filter(
            status=Invitation.ERROR,
        )[:4]

        for invite in invites_to_send:
            message = {'id': invite.id}
            send_invite(message)
