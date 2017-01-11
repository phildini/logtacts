from django.test import TestCase
from django.core.exceptions import ValidationError
import contacts as contact_constants
from contacts import forms
from contacts import factories
from contacts import models


class ContactFormTests(TestCase):

    def setUp(self):
        self.book = factories.BookFactory.create()
        self.tag = factories.TagFactory.create(book=self.book)
        self.contact = factories.ContactFactory(book=self.book)
        self.tag_choices = [(self.tag.id, self.tag.tag)]

    def test_form_without_book(self):
        with self.assertRaises(KeyError):
            form = forms.ContactForm()

    def test_form_valid_with_valid_data(self):
        form = forms.ContactForm(
            {'name': 'Philip James',}, 
            book=self.book,
            tag_choices=self.tag_choices,
        )
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_invalid_data(self):
        form = forms.ContactForm(book=self.book,tag_choices=self.tag_choices)
        self.assertFalse(form.is_valid())

    def test_correct_tags_in_form(self):
        form = forms.ContactForm(
            {'name': 'Philip James',}, 
            book=self.book,
            tag_choices=self.tag_choices,
        )
        bad_tag = factories.TagFactory.create()
        correct_choices = [(self.tag.id, self.tag.tag)]
        self.assertEqual(form.fields['tags'].choices, correct_choices)

    def test_form_field_creation(self):
        form_data = {
            'document_email_1': 'hello@hello.com',
            'document_email_1_label': 'Email',
            'document_email_1_pref': True,
            'name': 'Philip James',
        }
        form = forms.ContactForm(
            book=self.book,
            tag_choices=self.tag_choices,
            data=form_data
        )
        self.assertTrue('document_email_1' in form.fields)
        self.assertTrue('document_email_1_label' in form.fields)
        self.assertTrue('document_email_1_pref' in form.fields)

    def test_form_save_existing_field_email(self):
        field = factories.ContactFieldFactory(contact=self.contact)
        field.save()
        form_data = {
            'name': 'Philip James',
            'document_email_{}'.format(field.id): 'philip+test@contactotter.com',
            'document_email_{}_label'.format(field.id): 'New email',
            'document_email_{}_pref'.format(field.id): '[on]',
        }
        form = forms.ContactForm(
            book=self.book,
            data=form_data,
            tag_choices=self.tag_choices,
            instance=self.contact,
        )
        self.assert_(form.is_valid())
        form.save()
        field = models.ContactField.objects.get(id=field.id)
        self.assertEqual(field.value, 'philip+test@contactotter.com')
        self.assertEqual(field.label, 'New email')

    def test_form_save_existing_field_email(self):
        field = factories.ContactFieldFactory(
            contact=self.contact,
            kind=contact_constants.FIELD_TYPE_DATE,
            value='2015-01-01',
        )
        field.save()
        form_data = {
            'name': 'Philip James',
            'document_date_{}'.format(field.id): '2016-01-01',
            'document_date_{}_label'.format(field.id): 'New date',
            'document_date_{}_pref'.format(field.id): '[on]',
        }
        form = forms.ContactForm(
            book=self.book,
            data=form_data,
            tag_choices=self.tag_choices,
            instance=self.contact,
        )
        self.assert_(form.is_valid())
        form.save()
        field = models.ContactField.objects.get(id=field.id)
        self.assertEqual(field.value, '2016-01-01')
        self.assertEqual(field.label, 'New date')

    def test_form_save_existing_field_url(self):
        field = factories.ContactFieldFactory(
            contact=self.contact,
            kind=contact_constants.FIELD_TYPE_URL,
            value='http://www.logtacts.com',
        )
        field.save()
        form_data = {
            'name': 'Philip James',
            'document_url_{}'.format(field.id): 'http://www.contactotter.com',
            'document_url_{}_label'.format(field.id): 'New URL',
            'document_url_{}_pref'.format(field.id): '[on]',
        }
        form = forms.ContactForm(
            book=self.book,
            data=form_data,
            tag_choices=self.tag_choices,
            instance=self.contact,
        )
        self.assert_(form.is_valid())
        form.save()
        field = models.ContactField.objects.get(id=field.id)
        self.assertEqual(field.value, 'http://www.contactotter.com')
        self.assertEqual(field.label, 'New URL')

    def test_form_save_existing_field_duplicate_url_pref(self):
        form_data = {
            'name': 'Philip James',
            'document_url_new.1': 'http://www.contactotter.com',
            'document_url_new.1_label': 'New URL',
            'document_url_new.1_pref': '[on]',
            'document_url_new.2': 'http://www.contactotter.com',
            'document_url_new.2_label': 'New URL',
            'document_url_new.2_pref': '[on]',
        }
        form = forms.ContactForm(
            book=self.book,
            data=form_data,
            tag_choices=self.tag_choices,
            instance=self.contact,
        )
        self.assertFalse(form.is_valid())
        with self.assertRaises(ValueError):
            form.save()

    def test_form_save_existing_field_duplicate_phone_pref(self):
        form_data = {
            'name': 'Philip James',
            'document_phone_new.1': '4158675309',
            'document_phone_new.1_label': 'New phone',
            'document_phone_new.1_pref': '[on]',
            'document_phone_new.2': '4158675309',
            'document_phone_new.2_label': 'New phone',
            'document_phone_new.2_pref': '[on]',
        }
        form = forms.ContactForm(
            book=self.book,
            data=form_data,
            tag_choices=self.tag_choices,
            instance=self.contact,
        )
        self.assertFalse(form.is_valid())
        with self.assertRaises(ValueError):
            form.save()

    def test_form_save_existing_field_duplicate_email_pref(self):
        form_data = {
            'name': 'Philip James',
            'document_email_new.1': 'philip@contactotter.com',
            'document_email_new.1_label': 'New email',
            'document_email_new.1_pref': '[on]',
            'document_email_new.2': 'philip@contactotter.com',
            'document_email_new.2_label': 'New email',
            'document_email_new.2_pref': '[on]',
        }
        form = forms.ContactForm(
            book=self.book,
            data=form_data,
            tag_choices=self.tag_choices,
            instance=self.contact,
        )
        self.assertFalse(form.is_valid())
        with self.assertRaises(ValueError):
            form.save()

    def test_form_save_existing_field_duplicate_twitter_pref(self):
        form_data = {
            'name': 'Philip James',
            'document_twitter_new.1': '@phildini',
            'document_twitter_new.1_label': 'New twitter',
            'document_twitter_new.1_pref': '[on]',
            'document_twitter_new.2': '@phildini',
            'document_twitter_new.2_label': 'New twitter',
            'document_twitter_new.2_pref': '[on]',
        }
        form = forms.ContactForm(
            book=self.book,
            data=form_data,
            tag_choices=self.tag_choices,
            instance=self.contact,
        )
        self.assertFalse(form.is_valid())
        with self.assertRaises(ValueError):
            form.save()

    def test_form_save_existing_field_duplicate_address_pref(self):
        form_data = {
            'name': 'Philip James',
            'document_address_new.1': '1600 Pennsylvania Ave.',
            'document_address_new.1_label': 'New address',
            'document_address_new.1_pref': '[on]',
            'document_address_new.2': '1600 Pennsylvania Ave.',
            'document_address_new.2_label': 'New address',
            'document_address_new.2_pref': '[on]',
        }
        form = forms.ContactForm(
            book=self.book,
            data=form_data,
            tag_choices=self.tag_choices,
            instance=self.contact,
        )
        self.assertFalse(form.is_valid())
        with self.assertRaises(ValueError):
            form.save()

    def test_form_deleted_fields(self):
        field1 = factories.ContactFieldFactory(
            contact=self.contact,
            kind=contact_constants.FIELD_TYPE_URL,
            value='http://www.logtacts.com',
        )
        field2 = factories.ContactFieldFactory(
            contact=self.contact,
            kind=contact_constants.FIELD_TYPE_URL,
            value='http://www.logtacts.com',
        )
        field3 = factories.ContactFieldFactory(
            contact=self.contact,
            kind=contact_constants.FIELD_TYPE_URL,
            value='http://www.logtacts.com',
        )
        form_data = {
            'name': 'Philip James',
            'deleted_fields': '{},{},{}'.format(field1.id, field2.id, 20)
        }
        form = forms.ContactForm(
            book=self.book,
            data=form_data,
            tag_choices=self.tag_choices,
            instance=self.contact,
        )
        form.is_valid()
        form.save()
        self.assertEquals(
            len(models.ContactField.objects.filter(contact=self.contact)),
            1,
        )
        self.assertEquals(
            models.ContactField.objects.get(contact=self.contact),
            field3,
        )


class LogEntryFormTests(TestCase):

    def setUp(self):
        self.book = factories.BookFactory.create()
        self.contact = factories.ContactFactory.create(book=self.book)

    def test_form_valid_with_valid_data(self):
        form = forms.LogEntryForm({
            'contact': self.contact.id,
            'kind': 'twitter',
        })
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_invalid_data(self):
        form = forms.LogEntryForm()
        self.assertFalse(form.is_valid())


class TagFormTests(TestCase):

    def setUp(self):
        self.book = factories.BookFactory.create()

    def test_form_valid_with_valid_data(self):
        form = forms.TagForm({
            'tag':'tag',
        })
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_invalid_data(self):
        form = forms.TagForm()
        self.assertFalse(form.is_valid())

    def test_color_too_long_raises_error(self):
        form = forms.TagForm({
            'color':'1234567',
        })
        self.assertFalse(form.is_valid())


class MultiTagFormTests(TestCase):

    def setUp(self):
        self.book = factories.BookFactory.create()

    def test_create_form(self):
        contacts = factories.ContactFactory.create_batch(size=3)
        form = forms.MultiTagForm(
            tag_ids=[contact.id for contact in contacts],
        )
        self.assertEqual(len(form.fields), 3)
