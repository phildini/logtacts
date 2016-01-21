import logging
import requests
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.utils import timezone
from contacts.models import Contact
from profiles.models import Profile

logger = logging.getLogger('scripts')

class Command(BaseCommand):
    help = "send reminder for contacts to contact"

    def handle(self, *args, **options):
        last_month = timezone.now() - timedelta(weeks=4)
        profiles_opted_in = Profile.objects.filter(send_contact_reminders=True)
        for profile in profiles_opted_in:
            contact = Contact.objects.get_contacts_for_user(
                profile.user
            ).filter(
                last_contact__lte=last_month,
                should_surface=True,
            ).order_by('?')[0]
            subject = '[Logtacts] Contact reminder'
            body = (
                "You haven't contacted %s (https://%s/%s) in since %s - maybe send them a note?"
            ) % (
                contact.name,
                Site.objects.get_current().domain,
                contact.id,
                contact.last_contact,
            )
            import pdb; pdb.set_trace()
            try:
                message = EmailMessage(
                    subject=subject,
                    body=body,
                    from_email="reminders@logtacts.com",
                    to=[profile.user.email],
                )
                message.send()
            except:
                logger.exception('Problem sending reminder for %s' % (profile))

                try:
                    if not settings.DEBUG:
                        payload = {
                            'text': 'Error in logtacts remidner: {}'.format(profile)
                        }
                        r = requests.post(
                            settings.SLACK_WEBHOOK_URL,
                            data=json.dumps(payload),
                        )
                except:
                    logger.exception("Error sending error to slack")
