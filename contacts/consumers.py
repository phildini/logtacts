import datetime
import logging
from email.utils import parseaddr
import os
import requests
import vobject

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

sentry = logging.getLogger("raven")
logger = logging.getLogger("loggly_logs")


def process_incoming_email(message):
    _, sender = parseaddr(message.get('sender', ''))
    _, recipient = parseaddr(message.get('recipient', ''))

    try:
        user = User.objects.get(email=sender)
    except User.DoesNotExist:
        pass

    try:
        book_id = recipient.split('@')[0].split('-')[-1]
        book = Book.objects.filter_for_user(user, id=book_id)[0]
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
    try:
        url = message.get('url')
        local_filename = url.split('/')[-1]
        r = requests.get(url)
        with open(local_filename, 'wb') as f:
            f.write(r.content)
        with open(local_filename, 'r') as f:
            count = 0
            cards = []
            current_lines = []
            possible_keys = set()
            for line in f:
                if line.strip() == 'END:VCARD':
                    current_lines.append(line)
                    card = ''.join(current_lines)
                    cards.append(card)
                    count += 1
                    current_lines = []
                else:
                    current_lines.append(line)
            for card in cards:
                v = vobject.readOne(card)
                try:
                    name = str(v.n.value).strip()
                    if name:
                        contact = Contact.objects.create(book=book, name=name)
                        log = LogEntry.objects.create(contact=contact, kind='edit', logged_by=user)
                        contact.update_last_contact_from_log(log)
                        contact.save()
                    else:
                        continue
                except:
                    continue
                try:
                    for adr in v.adr_list:
                        field = ContactField.objects.create(
                            contact=contact,
                            label='Address',
                            kind='address',
                            value=str(adr.value),
                        )
                        field.save()
                except:
                    pass
                try:
                    for email in v.email_list:
                        field = ContactField.objects.create(
                            contact=contact,
                            label='Email',
                            kind='email',
                            value=str(email.value),
                        )
                        field.save()
                except:
                    pass
                try:
                    for url in v.url_list:
                        field = ContactField.objects.create(
                            contact=contact,
                            label='URL',
                            kind='url',
                            value=str(url.value),
                        )
                        field.save()
                except:
                    pass
                try:
                    for bday in v.bday_list:
                        field = ContactField.objects.create(
                            contact=contact,
                            label='Birthday',
                            kind='date',
                            value=str(bday.value),
                        )
                        field.save()
                except:
                    pass
                try:
                    for org in v.org_list:
                        if isinstance(org.value, list):
                            org = str(org.value[0])
                        else:
                            org = str(org.value)
                        field =ContactField.objects.create(
                            contact=contact,
                            label='Organization',
                            kind='text',
                            value=str(org),
                        )
                        field.save()
                except:
                    pass
                try:
                    for title in v.title_list:
                        field = ContactField.objects.create(
                            contact=contact,
                            label='Title',
                            kind='text',
                            value=str(title.value),
                        )
                        field.save()
                except:
                    pass        
        os.remove(local_filename)
    except Exception as e:
        sentry.error("Error processing vCard upload", exc_info=True)
