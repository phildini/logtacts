from django.test import TestCase
from contacts.consumers import process_incoming_email
from contacts import factories
from contacts import models

from common.factories import UserFactory


class ProcessEmailTests(TestCase):

    def setUp(self):
        self.book = factories.BookFactory.create()
        self.user = UserFactory.create(email='philip@inkpebble.com')
        factories.BookOwnerFactory.create(user=self.user, book=self.book)
        self.contact = factories.ContactFactory.create(
            name="Philip James", book=self.book,
        )
        factories.ContactFieldFactory.create(
            contact=self.contact,
            kind='email',
            value='phildini@phildini.net',
            label='email',
        )
        # Creating this twice because there was a bug
        factories.ContactFieldFactory.create(
            contact=self.contact,
            kind='email',
            value='phildini@phildini.net',
            label='email',
        )

    def test_basic_case(self):

        message = {
            'sender': 'philip@inkpebble.com',
            'recipient': 'log-1@mg.contactotter.com',
            'To': 'nicholle@inkpebble.com',
            'Cc': 'phildini@phildini.net',
            'subject': 'This is a test',
        }
        self.assertEqual(1, len(models.Contact.objects.filter(book=self.book)))

        process_incoming_email(message)

        self.assertEqual(2, len(models.Contact.objects.filter(book=self.book)), "More than 1 contact created")
        new_contact = models.ContactField.objects.get(value='nicholle@inkpebble.com', contact__book=self.book).contact
        self.assertEqual(1, len(models.LogEntry.objects.filter(contact=new_contact)), "New contact has >1 log")
        self.assertEqual(1, len(models.LogEntry.objects.filter(contact=self.contact)), "Old contact has >1 log")

    def test_google_groups(self):

        message = {
            'sender': 'philip@inkpebble.com',
            'recipient': 'log-1@mg.contactotter.com',
            'To': 'nicholle@inkpebble.com',
            'Cc': 'phildini@phildini.net, "Inkpebble Users Group" <ink@googlegroups.com>',
            'subject': 'This is a test',
        }
        self.assertEqual(1, len(models.Contact.objects.filter(book=self.book)))

        process_incoming_email(message)

        self.assertEqual(2, len(models.Contact.objects.filter(book=self.book)), "More than 1 contact created")
        new_contact = models.ContactField.objects.get(value='nicholle@inkpebble.com', contact__book=self.book).contact
        self.assertEqual(1, len(models.LogEntry.objects.filter(contact=new_contact)), "New contact has >1 log")
        self.assertEqual(1, len(models.LogEntry.objects.filter(contact=self.contact)), "Old contact has >1 log")
        self.assertEqual(1, len(models.Tag.objects.for_user(user=self.user, book=self.book)), "Wrong number of tags")
        self.assertEqual(1, len(new_contact.tags.all()), "Wrong number of tags on contact")