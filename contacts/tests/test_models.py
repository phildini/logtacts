from django.test import TestCase
from django.core.urlresolvers import reverse 
from common.factories import UserFactory
import contacts as contact_constants
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
        expected_url = reverse('contacts-view', kwargs={
            'pk': self.contact.id,
            'book': self.book.id,
        })
        self.assertEqual(self.contact.get_absolute_url(), expected_url)

    def test_contact_last_contacted(self):
        log = factories.LogFactory.create(contact=self.contact)
        self.contact.update_last_contact_from_log(log)

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

    def test_preferred_address_with_preferred(self):
        field = factories.ContactFieldFactory(
            contact=self.contact,
            kind=contact_constants.FIELD_TYPE_ADDRESS,
            value='1600 Pennsylvania Ave.',
            preferred=True,
        )
        self.assertEqual(self.contact.preferred_address, field.value)

    def test_preferred_address_without_preferred(self):
        field = factories.ContactFieldFactory(
            contact=self.contact,
            kind=contact_constants.FIELD_TYPE_ADDRESS,
            value='1600 Pennsylvania Ave.',
        )
        self.assertEqual(self.contact.preferred_address, field.value)

    def test_preferred_address_no_address(self):
        self.assertEqual(self.contact.preferred_address, '')

    def test_preferred_email_with_preferred(self):
        field = factories.ContactFieldFactory(
            contact=self.contact,
            kind=contact_constants.FIELD_TYPE_EMAIL,
            value='1600 Pennsylvania Ave.',
            preferred=True,
        )
        self.assertEqual(self.contact.preferred_email, field.value)

    def test_preferred_email_without_preferred(self):
        field = factories.ContactFieldFactory(
            contact=self.contact,
            kind=contact_constants.FIELD_TYPE_EMAIL,
            value='1600 Pennsylvania Ave.',
        )
        self.assertEqual(self.contact.preferred_email, field.value)

    def test_preferred_email_no_email(self):
        self.assertEqual(self.contact.preferred_email, '')

    def test_preferred_phone_with_preferred(self):
        field = factories.ContactFieldFactory(
            contact=self.contact,
            kind=contact_constants.FIELD_TYPE_PHONE,
            value='1600 Pennsylvania Ave.',
            preferred=True,
        )
        self.assertEqual(self.contact.preferred_phone, field.value)

    def test_preferred_phone_without_preferred(self):
        field = factories.ContactFieldFactory(
            contact=self.contact,
            kind=contact_constants.FIELD_TYPE_PHONE,
            value='1600 Pennsylvania Ave.',
        )
        self.assertEqual(self.contact.preferred_phone, field.value)

    def test_preferred_phone_no_phone(self):
        self.assertEqual(self.contact.preferred_phone, '')


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

    def test_corrected_color(self):
        self.assertEqual(self.tag.corrected_color, '#123456')
        self.tag.color = '#c0ffee'
        self.assertEqual(self.tag.corrected_color, '#c0ffee')
        self.tag.color = 'c0ffee'
        self.assertEqual(self.tag.corrected_color, '#c0ffee')


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
        self.contact.update_last_contact_from_log(self.log)

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
        self.contact.update_last_contact_from_log(self.log)
        self.assertEqual(self.log.created, self.contact.last_contact)



class ContactFieldModelTests(TestCase):

    def test_for_user(self):
        book = factories.BookFactory.create()
        user = UserFactory.create()
        contact = factories.ContactFactory.create(book=book)
        bookowner = factories.BookOwnerFactory.create(user=user,book=book)
        contactField1 = factories.ContactFieldFactory.create(contact=contact)
        contactField2 = factories.ContactFieldFactory.create()
        fields = models.ContactField.objects.for_user(user=user)
        self.assertEqual(1, len(fields))
