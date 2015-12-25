from django.test import TestCase
from django.core.urlresolvers import reverse 
from utils.factories import UserFactory
from contacts import factories
from contacts import models

class ContactModelTests(TestCase):

    def setUp(self):
        self.book = factories.BookFactory.create()
        self.contact = factories.ContactFactory.create(
            name="Philip James",
            book=self.book,
        )

    def test_contact_name(self):
        """String repr of contact should be name."""

        self.assertEqual(self.contact.name, str(self.contact))

    def test_contact_url(self):
        expected_url = reverse('contacts-view', kwargs={'pk': self.contact.id})
        self.assertEqual(self.contact.get_absolute_url(), expected_url)

    def test_contact_last_contacted(self):
        log = factories.LogFactory.create(contact=self.contact)

        self.assertEqual(self.contact.last_contacted(), log.created)

    def test_contact_can_be_viewed_by(self):
        bookowner = factories.BookOwnerFactory.create(book=self.book)
        user = bookowner.user
        self.assertTrue(self.contact.can_be_viewed_by(user))

    def test_contact_can_be_edited_by(self):
        bookowner = factories.BookOwnerFactory.create(book=self.book)
        user = bookowner.user
        self.assertTrue(self.contact.can_be_edited_by(user))


class TagModelTests(TestCase):

    def setUp(self):
        self.contact = factories.ContactFactory.create(
            name="Philip James",
        )

    def test_tag_name(self):
        tag = factories.TagFactory.create(tag='Family')
        self.assertEqual(tag.tag, str(tag))


class BookModelTests(TestCase):

    def test_book_name(self):
        book = factories.BookFactory.create(name="James Family")
        self.assertEqual(book.name, str(book))


class BookOwnerModelTests(TestCase):

    def setUp(self):
        self.book = factories.BookFactory.create(name="James Family")
        self.user = UserFactory(username="phildini")

    def test_book_owner_repr(self):
        bookowner = factories.BookOwnerFactory(book=self.book, user=self.user)
        expected = "{} is an owner of {}".format(self.user, self.book)
        self.assertEqual(str(bookowner), expected)


class LogEntryModelTests(TestCase):

    def setUp(self):
        self.contact = factories.ContactFactory.create(
            name="Philip James",
        )

    def test_tag_repr(self):
        log = factories.LogFactory.create(contact=self.contact)
        expected = "Log on %s" % (self.contact)
        self.assertEqual(str(log), expected)
