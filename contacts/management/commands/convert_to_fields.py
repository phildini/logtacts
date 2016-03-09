import logging
from django.utils import timezone
from django.core.management.base import BaseCommand

import contacts as contact_settings
from contacts.models import Contact, ContactField

logger = logging.getLogger('scripts')

class Command(BaseCommand):
    help = "Convert old-style contacts to new-style contacts"

    def handle(self, *args, **kwargs):
        contacts = Contact.objects.all()
        for contact in contacts:
            if contact.email:
                ContactField.objects.get_or_create(
                    label='Email',
                    kind=contact_settings.FIELD_TYPE_EMAIL,
                    value=contact.email,
                    preferred=True,
                    contact=contact,
                )
            if contact.twitter:
                ContactField.objects.get_or_create(
                    label='Twitter',
                    kind=contact_settings.FIELD_TYPE_TWITTER,
                    value=contact.twitter,
                    preferred=True,
                    contact=contact,
                )
            if contact.tumblr:
                ContactField.objects.get_or_create(
                    label='Tumblr',
                    kind=contact_settings.FIELD_TYPE_TEXT,
                    value=contact.tumblr,
                    contact=contact,
                )
            if contact.website:
                ContactField.objects.get_or_create(
                    label='Website',
                    kind=contact_settings.FIELD_TYPE_URL,
                    value=contact.website,
                    contact=contact,
                )
            if contact.portfolio:
                ContactField.objects.get_or_create(
                    label='Portfolio',
                    kind=contact_settings.FIELD_TYPE_URL,
                    value=contact.portfolio,
                    contact=contact,
                )
            if contact.cell_phone:
                ContactField.objects.get_or_create(
                    label='Cell Phone',
                    kind=contact_settings.FIELD_TYPE_PHONE,
                    value=contact.cell_phone,
                    preferred=True,
                    contact=contact,
                )
            if contact.home_phone:
                ContactField.objects.get_or_create(
                    label='Home Phone',
                    kind=contact_settings.FIELD_TYPE_PHONE,
                    value=contact.home_phone,
                    contact=contact,
                )
            if contact.company:
                ContactField.objects.get_or_create(
                    label='Company',
                    kind=contact_settings.FIELD_TYPE_TEXT,
                    value=contact.company,
                    contact=contact,
                )
            if contact.address:
                ContactField.objects.get_or_create(
                    label='Address',
                    kind=contact_settings.FIELD_TYPE_ADDRESS,
                    value=contact.address,
                    preferred=True,
                    contact=contact,
                )
            if contact.birthday:
                ContactField.objects.get_or_create(
                    label='Birthday',
                    kind=contact_settings.FIELD_TYPE_DATE,
                    value=contact.birthday,
                    contact=contact,
                )
            if contact.work_phone:
                ContactField.objects.get_or_create(
                    label='Work Phone',
                    kind=contact_settings.FIELD_TYPE_PHONE,
                    value=contact.work_phone,
                    contact=contact,
                )
            if contact.work_email:
                ContactField.objects.get_or_create(
                    label='Work Email',
                    kind=contact_settings.FIELD_TYPE_EMAIL,
                    value=contact.work_email,
                    contact=contact,
                )
