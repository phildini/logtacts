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

    def test_contact_cant_be_viewed_by_bad(self):
        user = UserFactory.create(username='asheesh')
        self.assertFalse(self.contact.can_be_viewed_by(user))

    def test_contact_cant_be_edited_by_bad(self):
        user = UserFactory.create(username='asheesh')
        self.assertFalse(self.contact.can_be_edited_by(user))

    def test_get_contacts_for_user(self):
        bookowner = factories.BookOwnerFactory.create(book=self.book)
        user = bookowner.user
        self.assertEqual(
            [self.contact],
            list(models.Contact.objects.get_contacts_for_user(user)),
        )

    def test_get_contacts_for_user_bad_user(self):
        user = UserFactory.create(username="nicholle")
        self.assertFalse(
            list(models.Contact.objects.get_contacts_for_user(user)),
        )


class TagModelTests(TestCase):

    def setUp(self):
        self.book = factories.BookFactory.create()
        self.contact = factories.ContactFactory.create(
            name="Philip James",
            book=self.book,
        )
        self.tag = factories.TagFactory.create(
            tag='Family',
            book=self.book,
        )

    def test_tag_name(self):
        self.assertEqual(self.tag.tag, str(self.tag))

    def test_get_tags_for_user(self):
        bookowner = factories.BookOwnerFactory.create(book=self.book)
        user = bookowner.user
        self.assertEqual(
            [self.tag],
            list(models.Tag.objects.get_tags_for_user(user)),
        )

    def test_tag_can_be_viewed_by(self):
        bookowner = factories.BookOwnerFactory.create(book=self.book)
        user = bookowner.user
        self.assertTrue(self.tag.can_be_viewed_by(user))

    def test_tag_can_be_edited_by(self):
        bookowner = factories.BookOwnerFactory.create(book=self.book)
        user = bookowner.user
        self.assertTrue(self.tag.can_be_edited_by(user))

    def test_tag_cant_be_viewed_by_bad(self):
        user = UserFactory.create(username='asheesh')
        self.assertFalse(self.tag.can_be_viewed_by(user))

    def test_tag_cant_be_edited_by_bad(self):
        user = UserFactory.create(username='asheesh')
        self.assertFalse(self.tag.can_be_edited_by(user))


class BookModelTests(TestCase):

    def setUp(self):
        self.book = factories.BookFactory.create(name="James Family")

    def test_book_name(self):
        self.assertEqual(self.book.name, str(self.book))

    def test_book_can_be_viewed_by(self):
        bookowner = factories.BookOwnerFactory.create(book=self.book)
        user = bookowner.user
        self.assertTrue(self.book.can_be_viewed_by(user))

    def test_book_can_be_edited_by(self):
        bookowner = factories.BookOwnerFactory.create(book=self.book)
        user = bookowner.user
        self.assertTrue(self.book.can_be_edited_by(user))

    def test_book_cant_be_viewed_by_bad(self):
        user = UserFactory.create(username='asheesh')
        self.assertFalse(self.book.can_be_viewed_by(user))

    def test_book_cant_be_edited_by_bad(self):
        user = UserFactory.create(username='asheesh')
        self.assertFalse(self.book.can_be_edited_by(user))


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
        self.book = factories.BookFactory.create(name="James Family")
        self.user = UserFactory(username="phildini")
        self.bookowner = factories.BookOwnerFactory(book=self.book, user=self.user)
        self.contact = factories.ContactFactory.create(
            name="Philip James",
            book=self.book,
        )
        self.log = factories.LogFactory.create(contact=self.contact)

    def test_tag_repr(self):
        expected = "Log on %s" % (self.contact)
        self.assertEqual(str(self.log), expected)

    def test_log_can_be_viewed_by(self):
        bookowner = factories.BookOwnerFactory.create(book=self.book)
        user = bookowner.user
        self.assertTrue(self.log.can_be_viewed_by(user))

    def test_log_can_be_edited_by(self):
        bookowner = factories.BookOwnerFactory.create(book=self.book)
        user = bookowner.user
        self.assertTrue(self.log.can_be_edited_by(user))

    def test_log_cant_be_viewed_by_bad(self):
        user = UserFactory.create(username='asheesh')
        self.assertFalse(self.log.can_be_viewed_by(user))

    def test_log_cant_be_edited_by_bad(self):
        user = UserFactory.create(username='asheesh')
        self.assertFalse(self.log.can_be_edited_by(user))

    def test_creating_log_updates_contact(self):
        self.assertTrue(self.contact.last_contact)
        self.assertEqual(self.log.created, self.contact.last_contact)

    def test_creating_edit_log_no_contact_update(self):
        edit_log = factories.LogFactory.create(kind='edit', contact=self.contact)
        self.assertEqual(self.log.created, self.contact.last_contact)
