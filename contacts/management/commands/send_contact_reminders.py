import json
import logging
import requests
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import get_template
from django.utils import timezone
import contacts as contact_constants
from contacts.models import (
    Contact,
    ContactField,
)
from profiles.models import Profile

logger = logging.getLogger('scripts')

class Command(BaseCommand):
    help = "send reminder for contacts to contact"

    def handle(self, *args, **options):
        logger.debug("Starting contact reminder sending")
        last_month = timezone.now() - timedelta(weeks=4)
        profiles_opted_in = Profile.objects.filter(send_contact_reminders=True)
        for profile in profiles_opted_in:
            logger.debug("Starting compilation for {}".format(profile.user))
            contact = Contact.objects.get_contacts_for_user(
                profile.user
            ).filter(
                Q(last_contact__lte=last_month) | Q(last_contact=None),
                should_surface=True,
            ).order_by('?')[0]
            subject = '[Contact Otter] Contact reminder'
            context = {
                'contact': contact,
                'domain': Site.objects.get_current().domain,

            }
            txt = get_template('email/contact_reminder.txt').render(context)
            html = get_template('email/contact_reminder.html').render(context)
            message = EmailMultiAlternatives(
                subject=subject,
                body=txt,
                from_email="ContactOtter <reminders@contactotter.com>",
                to=[profile.user.email],
            )
            message.attach_alternative(html, "text/html")
            try:
                logger.debug("Trying to send message to {} about {}".format(
                    profile.user, contact
                ))
                message.send()
                logger.debug("Sent message to {} successfuly".format(profile.user))
            except:
                logger.exception('Problem sending reminder for %s' % (profile))
                try:
                    if not settings.DEBUG:
                        payload = {
                            'text': 'Error in contactotter reminder: {}'.format(profile)
                        }
                        r = requests.post(
                            settings.SLACK_WEBHOOK_URL,
                            data=json.dumps(payload),
                        )
                except:
                    logger.exception("Error sending error to slack")

        profiles_opted_in = Profile.objects.filter(send_birthday_reminders=True)
        for profile in profiles_opted_in:
            birthdays = ContactField.objects.filter(
                Q(label='Birthday') | Q(label='birthday') | Q(label='BIRTHDAY'),
                kind=contact_constants.FIELD_TYPE_DATE,
                value=timezone.now().strftime("%Y-%m-%d")
            )
            contacts = None
            if birthdays:
                contacts = [birthday.contact for birthday in birthdays]
            if contacts:
                context = {
                    'contacts': contacts,
                    'domain': Site.objects.get_current().domain,
                }
                subject="[ContactOtter] Birthday reminder"
                txt = get_template('email/birthday_reminder.txt').render(context)
                html = get_template('email/birthday_reminder.html').render(context)
                message = EmailMultiAlternatives(
                    subject=subject,
                    body=txt,
                    from_email='ContactOtter <reminders@contactotter.com>',
                    to=[profile.user.email],
                )
                message.attach_alternative(html, "text/html")
                try:
                    logger.debug("Trying to send message to {} about {}".format(
                        profile.user, contact
                    ))
                    message.send()
                    logger.debug("Sent message to {} successfuly".format(profile.user))
                except:
                    logger.exception('Problem sending reminder for %s' % (profile))
                    try:
                        if not settings.DEBUG:
                            payload = {
                                'text': 'Error in logtacts reminder: {}'.format(profile)
                            }
                            r = requests.post(
                                settings.SLACK_WEBHOOK_URL,
                                data=json.dumps(payload),
                            )
                    except:
                        logger.exception("Error sending error to slack")
