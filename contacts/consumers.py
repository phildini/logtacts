import datetime
import logging
from email.utils import parseaddr

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils import timezone

import contacts as contact_settings
from contacts.models import (
    Book,
    Contact,
    ContactField,
    LogEntry,
)
from .utils import pull_google_contacts

sentry = logging.getLogger("sentry")


def import_google_contacts(message):
    try:
        user = User.objects.get(id=message.get('user_id'))
        book = Book.objects.get(bookowner__user=user, id=message.get('book_id'))
    except Book.DoesNotExist:
        sentry.error("Bad book passed to google import job", exc_info=True)
        return
    except User.DoesNotExist:
        sentry.error("Bad user passed to google import job", exc_info=True)
        return
    try:
        success = pull_google_contacts(user=user, book=book)
        success = True
        if success:
            cache.delete("{}::google-import".format(user))
            try:
                context = {
                    'domain': Site.objects.get_current().domain,
                }
                txt = get_template('email/google_import_done.txt').render(context)
                html = get_template('email/google_import_done.html').render(context)
                message = EmailMultiAlternatives(
                    subject='Contact import finished!',
                    body=txt,
                    from_email="ContactOtter <import@contactotter.com>",
                    to=[user.email],
                    headers={
                        'Reply-To': "ContactOtter <support@contactotter.com>",
                    },
                )
                message.attach_alternative(html, "text/html")
                message.send()
            except:
                sentry.error("Error sending import success email", exc_info=True)
    except:
        cache.set("{}::google-import".format(user), "error", 86400)


def process_incoming_email(message):
    _, sender = parseaddr(message.get('sender', ''))
    _, recipient = parseaddr(message.get('recipient', ''))

    try:
        user = User.objects.get(email=sender)
    except User.DoesNotExist:
        pass

    try:
        book_id = recipient.split('@')[0].split('-')[-1]
        book = Book.objects.filter_for_user(user).get(id=book_id)
    except (Book.DoesNotExist, IndexError):
        pass

    if not (user and book):
        return

    to = message.get('To', '').split(',')
    to += (message.get('Cc', '').split(','))
    to += (message.get('Bcc', '').split(','))
    for item in set(to):
        name, email = parseaddr(item)
        if email and email != recipient:
            try:
                contact = ContactField.objects.filter(
                    kind=contact_settings.FIELD_TYPE_EMAIL,
                    value=email,
                    contact__book=book,
                )[0].contact
            except (ContactField.DoesNotExist, IndexError):
                if not name:
                    name = email
                contact = Contact.objects.create(
                    name=name,
                    book=book,
                )
                ContactField.objects.create(
                    contact=contact,
                    kind=contact_settings.FIELD_TYPE_EMAIL,
                    value=email,
                    label="Email",
                    preferred=True,
                )
            LogEntry.objects.create(
                contact=contact,
                kind='email',
                logged_by=user,
                time=timezone.now(),
                notes='Subject: {}'.format(message.get('subject')),
            )

