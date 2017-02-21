import logging
import requests
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils import timezone

from invitations.models import Invitation

logger = logging.getLogger('email')
sentry = logging.getLogger('sentry')

def send_invite(message):
    try:
        invite = Invitation.objects.get(
            id=message.get('id'),
            status__in=[Invitation.PENDING, Invitation.ERROR],
        )
    except Invitation.DoesNotExist:
        sentry.error("Invitation to send not found", exc_info=True, extra={'message': message})
        return
    invite.status = Invitation.PROCESSING
    invite.save()
    context = {
        'invite': invite,
        'domain': Site.objects.get_current().domain,
    }
    subject = "[ContactOtter] Invitation to join ContactOtter from %s" % (invite.sender)
    if invite.book:
        subject = "[ContactOtter] Invitation to share %s's contact book" % (invite.sender)
    txt = get_template('email/invitation.txt').render(context)
    html = get_template('email/invitation.html').render(context)
    try:
        message = EmailMultiAlternatives(
            subject=subject,
            body=txt,
            from_email="ContactOtter <invites@contactotter.com>",
            to=[invite.email,],
        )
        message.attach_alternative(html, "text/html")
        message.send()
        invite.status = Invitation.SENT
        invite.sent = timezone.now()
        invite.save()
    except:
        sentry.exception('Problem sending invite', exc_info=True, extra={'invite_id': invite.id})
        invite.status = Invitation.ERROR
        invite.save()
