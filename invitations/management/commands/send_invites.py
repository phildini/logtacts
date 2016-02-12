import logging
import requests
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils import timezone


from invitations.models import Invitation

logger = logging.getLogger('scripts')

class Command(BaseCommand):
    help = "send invites"

    def handle(self, *args, **options):
        invites_to_send = Invitation.objects.filter(
            status=Invitation.PENDING
        )[:4]

        for invite in invites_to_send:
            logger.debug('Sending invite %s' % (invite.id))
            invite.status = Invitation.PROCESSING
            invite.save()
            if invite.book:
                subject = "[ContactOtter] Invitation to share %s's contact book" % (invite.sender)
                body = (
                        "%s has invited you to share their contact book on ContactOtter.\n"
                        "Go to https://%s/invites/accept/%s/ to join!"
                    ) % (
                        invite.sender,
                        Site.objects.get_current().domain,
                        invite.key,
                    )
            else:
                subject = "[ContactOtter] Invitation to join ContactOtter from %s" % (invite.sender)
                body = "Go to https://%s/invites/accept/%s/ to join!" % (
                        Site.objects.get_current().domain,
                        invite.key,
                    )
            try:
                message = EmailMessage(
                    subject=subject,
                    body=body,
                    from_email="ContactOtter <invites@contactotter.com>",
                    to=[invite.email,],
                )
                message.send()
                invite.status = Invitation.SENT
                invite.sent = timezone.now()
                invite.save()
            except:
                logger.exception('Problem sending invite %s' % (invite.id))
                invite.status = Invitation.ERROR
                invite.save()
                try:
                    if not settings.DEBUG:
                        payload = {
                            'text': 'Error in logtacts invite: {}'.format(job.id)
                        }
                        r = requests.post(
                            settings.SLACK_WEBHOOK_URL,
                            data=json.dumps(payload),
                        )
                except:
                    logger.exception("Error sending error to slack")


