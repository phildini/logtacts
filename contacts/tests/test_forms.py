from django.test import TestCase
from contacts import forms
from contacts import factories


class ContactFormTests(TestCase):

    def setUp(self):
        self.book = factories.BookFactory.create()
        self.tag = factories.TagFactory.create(book=self.book)

    def test_form_without_book(self):
        with self.assertRaises(KeyError):
            form = forms.ContactForm()

    def test_form_valid_with_valid_data(self):
        form = forms.ContactForm({
            'name': 'Philip James',
            }, book=self.book,
        )
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_invalid_data(self):
        form = forms.ContactForm(book=self.book)
        self.assertFalse(form.is_valid())

    def test_correct_tags_in_form(self):
        form = forms.ContactForm({
            'name': 'Philip James',
            }, book=self.book,
        )
        bad_tag = factories.TagFactory.create()
        correct_choices = [(self.tag.id, self.tag.tag)]
        self.assertEqual(form.fields['tags'].choices, correct_choices)


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
