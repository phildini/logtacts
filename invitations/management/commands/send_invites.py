import logging
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
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
                subject = "[Logtacts] Invitation to share %s's contact book" % (invite.sender)
                body = (
                        "%s has invited you to share their contact book on Logtacts.\n"
                        "Go to https://%s/invites/accept/%s/ to join!"
                    ) % (
                        invite.sender,
                        Site.objects.get_current().domain,
                        invite.key,
                    ),
            else:
                subject = "[Logtacts] Invitation to join Logtacts from %s" % (invite.sender)
                body = "Go to https://%s/invites/accept/%s/ to join!" % (
                        Site.objects.get_current().domain,
                        invite.key,
                    ),
            try:
                message = EmailMessage(
                    subject=subject,
                    body=body,
                    from_email="invites@logtacts.com",
                    to=[invite.email,],
                )
                message.send()
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
            invite.status = Invitation.SENT
            invite.sent = timezone.now()
            invite.save()


