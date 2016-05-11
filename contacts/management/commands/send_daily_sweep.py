import json
import logging
import requests
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from profiles.models import Profile

logger = logging.getLogger('scripts')


class Command(BaseCommand):
    help = "send daily sweep email"

    def handle(self, *args, **options):
        logger.debug("Starting daily sweep email job")
        profiles_opted_in = Profile.objects.filter(
            send_contact_reminders=True)
        for profile in profiles_opted_in:
            logger.debug("Starting compilation for {}".format(profile.user))
            subject = '[Contact Otter] Did you meet with anyone today?'
            context = {
                'domain': Site.objects.get_current().domain,
            }
            txt = get_template('email/daily_sweep.txt').render(context)
            html = get_template('email/daily_sweep.html').render(context)
            message = EmailMultiAlternatives(
                subject=subject,
                body=txt,
                from_email="ContactOtter <reminders@contactotter.com>",
                to=[profile.user.email],
            )
            message.attach_alternative(html, "text/html")
            try:
                logger.debug("Trying to send daily sweep to{}".format(profile.user))
                message.send()
                logger.debug("Sent message to {} successfuly".format(profile.user))
            except:
                logger.exception('Problem sending daily sweep for %s' % (profile))
                try:
                    if not settings.DEBUG:
                        payload = {
                            'text': 'Error in contactotter daily sweep: {}'.format(profile)
                        }
                        r = requests.post(
                            settings.SLACK_WEBHOOK_URL,
                            data=json.dumps(payload),
                        )
                except:
                    logger.exception("Error sending error to slack")
