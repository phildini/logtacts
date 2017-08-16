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
    Tag,
)
from .utils import pull_google_contacts

sentry = logging.getLogger("raven")


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
        sentry.error("Somehow we got an email without user or book", extra=message)
        return

    contacts_updated = []
    tag = None
    to = message.get('To', '').split(',')
    to += (message.get('Cc', '').split(','))
    to += (message.get('Bcc', '').split(','))
    for item in set(to):
        name, email = parseaddr(item)
        if email and email != recipient:
            email_parts = email.split('@')
            if len(email_parts) > 1 and email_parts[1] == 'googlegroups.com':
                tag_name = name if name else email_parts[0]
                tag = Tag.objects.create(
                    book=book,
                    tag=tag_name,
                )
                continue
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
            log=LogEntry.objects.create(
                contact=contact,
                kind='email',
                logged_by=user,
                time=timezone.now(),
                notes='Subject: {}'.format(message.get('subject')),
            )
            contact.update_last_contact_from_log(log)
            contacts_updated.append(contact)
    if tag and contacts_updated:
        for contact in contacts_updated:
            contact.tags.add(tag)
            contact.save()


def process_vcard_upload(message):
    try:
        user = User.objects.get(id=message.get('user_id'))
        book = Book.objects.get(bookowner__user=user, id=message.get('book_id'))
    except Book.DoesNotExist:
        sentry.error("Bad book passed to vCard import job", exc_info=True)
        return
    except User.DoesNotExist:
        sentry.error("Bad user passed to vCard import job", exc_info=True)
        return
    url = message.get('url')
    local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    with open(local_filename, 'r') as f:
        
