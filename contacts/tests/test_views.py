from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.http.response import Http404
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage

from common.factories import UserFactory

from contacts import factories
from contacts import models
from contacts import views


class ContactListViewTests(TestCase):

    def setUp(self):
        self.book = factories.BookFactory.create()
        request_factory = RequestFactory()
        request = request_factory.get(reverse('contacts-list', kwargs={'book': self.book.id}))
        request.user = UserFactory.create()
        request.current_book = self.book
        self.response = views.contact_list_views.ContactListView.as_view()(request)

    def test_contact_list_view_response_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_contact_list_view_renders(self):
        self.response.render()

    def test_contact_list_view_contains_only_what_it_should(self):
        user = UserFactory.create(username='nicholle')
        factories.BookOwnerFactory.create(book=self.book, user=user)
        good_contact = factories.ContactFactory.create(book=self.book)
        bad_contact = factories.ContactFactory.create()
        good_tag = factories.TagFactory.create(book=self.book)
        bad_tag = factories.TagFactory.create()
        good_contact.tags.add(good_tag)
        request_factory = RequestFactory()
        request = request_factory.get(reverse('contacts-list', kwargs={'book': self.book.id}))
        request.user = user
        request.current_book = self.book
        response = views.contact_list_views.ContactListView.as_view()(request)
        self.assertEqual(len(response.context_data.get('tags')), 1)
        self.assertEqual(len(response.context_data.get('contact_list')), 1)
        self.assertEqual(response.context_data.get('tags')[0], good_tag)
        self.assertEqual(
            response.context_data.get('contact_list')[0], good_contact,
        )


class ContactViewTests(TestCase):
    def setUp(self):
        self.book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(user=self.user, book=self.book)
        self.contact = factories.ContactFactory.create(book=self.book)
        self.request_factory = RequestFactory()
        self.request = self.request_factory.get(self.contact.get_absolute_url())
        self.request.current_book = self.book

    def test_contact_detail_view_response_200(self):
        self.request.user = self.user
        response = views.contact_views.ContactView.as_view()(
            self.request,
            pk=self.contact.pk,
        )
        self.assertEqual(response.status_code, 200)

    def test_contact_detail_view_404_wrong_user(self):
        self.request.user = UserFactory.create()
        with self.assertRaises(Http404):
            views.contact_views.ContactView.as_view()(
                self.request,
                pk=self.contact.pk,
            )

    def test_contact_detail_view_renders(self):
        self.request.user = self.user
        response = views.contact_views.ContactView.as_view()(
            self.request,
            pk=self.contact.pk,
        )
        response.render()

    def test_add_log_to_contact_missing_fields(self):
        self.request = self.request_factory.post(
            self.contact.get_absolute_url(),
        )
        self.request.user = self.user
        self.request.current_book = self.book
        response = views.contact_views.ContactView.as_view()(
            self.request,
            pk=self.contact.pk,
        )
        self.assertEqual(['This field is required.'], response.context_data['form'].errors['kind'])

    def test_add_log_to_contact(self):
        logs = models.LogEntry.objects.filter(contact=self.contact)
        self.assertEqual(0, len(logs))
        self.request = self.request_factory.post(
            self.contact.get_absolute_url(),
            {'kind': 'in person', 'notes': 'Met at DjangoCon!'}
        )
        self.request.user = self.user
        self.request.current_book = self.book
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)
        response = views.contact_views.ContactView.as_view()(
            self.request,
            pk=self.contact.pk,
        )
        self.assertEqual(302, response.status_code)
        logs = models.LogEntry.objects.filter(contact=self.contact)
        self.assertEqual(1, len(logs))


class EditContactViewTests(TestCase):

    def setUp(self):
        book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(user=self.user,book=book)
        self.contact = factories.ContactFactory.create(book=book)
        request_factory = RequestFactory()
        self.request = request_factory.get(
            reverse('contacts-edit', kwargs={'pk': self.contact.id, 'book': book.id}),
        )
        self.request.current_book = book


    def test_edit_contact_view_200(self):
        self.request.user = self.user
        response = views.contact_views.EditContactView.as_view()(
            self.request,
            pk=self.contact.pk,
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_contact_view_404_wrong_user(self):
        self.request.user = UserFactory.create()
        with self.assertRaises(Http404):
            views.contact_views.EditContactView.as_view()(
                self.request,
                pk=self.contact.pk,
            )

    def test_edit_contact_view_renders(self):
        self.request.user = self.user
        response = views.contact_views.EditContactView.as_view()(
            self.request,
            pk=self.contact.pk,
        )
        response.render()


class CreateContactViewTests(TestCase):

    def setUp(self):
        book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(user=self.user,book=book)
        request_factory = RequestFactory()
        self.request = request_factory.get(
            reverse('contacts-new', kwargs={'book': book.id}),
        )
        self.request.current_book = book


    def test_create_contact_view_200(self):
        self.request.user = self.user
        response = views.contact_views.CreateContactView.as_view()(
            self.request,
        )
        self.assertEqual(response.status_code, 200)

    def test_create_contact_view_renders(self):
        self.request.user = self.user
        response = views.contact_views.CreateContactView.as_view()(
            self.request,
        )
        response.render()


class LogViewTests(TestCase):

    def setUp(self):
        self.book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(user=self.user,book=self.book)
        self.contact = factories.ContactFactory.create(book=self.book)
        self.log = factories.LogFactory.create(contact=self.contact)
        self.request_factory = RequestFactory()

    def test_log_edit_view_200_if_right_user(self):
        self.request = self.request_factory.get(
            reverse('log-edit', kwargs={'pk': self.log.id, 'book': self.book.id})
        )
        self.request.user = self.user
        self.request.current_book = self.book
        response = views.log_views.EditLogView.as_view()(
            self.request,
            pk=self.log.pk,
        )
        self.assertEqual(response.status_code, 200)

    def test_log_edit_view_401_if_right_user(self):
        self.request = self.request_factory.get(
            reverse('log-edit', kwargs={'pk': self.log.id, 'book': self.book.id})
        )
        self.request.user = UserFactory.create()
        self.request.current_book = self.book
        with self.assertRaises(PermissionDenied):
            views.log_views.EditLogView.as_view()(
                self.request,
                pk=self.log.pk,
            )

    def test_log_edit_view_renders(self):
        self.request = self.request_factory.get(
            reverse('log-edit', kwargs={'pk': self.log.id, 'book': self.book.id})
        )
        self.request.user = self.user
        self.request.current_book = self.book
        response = views.log_views.EditLogView.as_view()(
            self.request,
            pk=self.log.pk,
        )
        response.render()

    def test_log_delete_view_200_if_right_user(self):
        self.request = self.request_factory.get(
            reverse('log-delete', kwargs={'pk': self.log.id, 'book': self.book.id})
        )
        self.request.user = self.user
        self.request.current_book = self.book
        response = views.log_views.DeleteLogView.as_view()(
            self.request,
            pk=self.log.pk,
        )
        self.assertEqual(response.status_code, 200)

    def test_log_delete_view_401_if_wrong_user(self):
        self.request = self.request_factory.get(
            reverse('log-delete', kwargs={'pk': self.log.id, 'book': self.book.id})
        )
        self.request.user = UserFactory.create()
        self.request.current_book = self.book
        with self.assertRaises(PermissionDenied):
            views.log_views.DeleteLogView.as_view()(
                self.request,
                pk=self.log.pk,
            )

    def test_log_delete_view_renders(self):
        self.request = self.request_factory.get(
            reverse('log-delete', kwargs={'pk': self.log.id, 'book': self.book.id})
        )
        self.request.user = self.user
        self.request.current_book = self.book
        response = views.log_views.DeleteLogView.as_view()(
            self.request,
            pk=self.log.pk,
        )
        response.render()


class TagViewTests(TestCase):

    def setUp(self):
        self.book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(user=self.user,book=self.book)
        self.contact = factories.ContactFactory.create(book=self.book)
        self.tag = factories.TagFactory.create(tag='Test', book=self.book)
        self.contact.tags.add(self.tag)
        self.request_factory = RequestFactory()

    def test_tagged_list_view_200(self):
        request = self.request_factory.get(
            reverse('contacts-tagged', kwargs={'pk': self.tag.id, 'book': self.book.id}),
        )
        request.user = self.user
        request.current_book = self.book
        response = views.contact_list_views.TaggedContactListView.as_view()(
            request,
            pk=self.tag.pk,
        )
        self.assertEqual(response.status_code, 200)

    def test_tagged_list_view_401_if_wrong_user(self):
        request = self.request_factory.get(
            reverse('contacts-tagged', kwargs={'pk': self.tag.id, 'book': self.book.id})
        )
        request.user = UserFactory.create()
        request.current_book = self.book
        with self.assertRaises(Http404):
            views.contact_list_views.TaggedContactListView.as_view()(
                request,
                pk=self.tag.pk,
            )

    def test_tagged_list_view_renders(self):
        request = self.request_factory.get(
            reverse('contacts-tagged', kwargs={'pk': self.tag.id, 'book': self.book.id}),
        )
        request.user = self.user
        request.current_book = self.book
        response = views.contact_list_views.TaggedContactListView.as_view()(
            request,
            pk=self.tag.pk,
        )
        response.render()

    def test_tagged_list_view_contains_only_what_it_should(self):
        tag = factories.TagFactory.create(tag='Test Bad')
        contact = factories.ContactFactory.create()
        request = self.request_factory.get(
            reverse('contacts-tagged', kwargs={'pk': self.tag.id, 'book': self.book.id}),
        )
        request.user = self.user
        request.current_book = self.book
        response = views.contact_list_views.TaggedContactListView.as_view()(
            request,
            pk=self.tag.pk,
        )
        self.assertEqual(len(response.context_data.get('tags')), 1)
        self.assertEqual(len(response.context_data.get('contact_list')), 1)


class CreateTagViewTests(TestCase):

    def setUp(self):
        self.book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(user=self.user,book=self.book)
        self.contact = factories.ContactFactory.create(book=self.book)
        self.request_factory = RequestFactory()

    def test_edit_tag_view_200(self):
        request = self.request_factory.get(
            reverse('tags-new', kwargs={'book': self.book.id}),
        )
        request.user = self.user
        request.current_book = self.book
        response = views.contact_views.CreateTagView.as_view()(
            request,
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_tag_view_renders(self):
        request = self.request_factory.get(
            reverse('tags-new', kwargs={'book': self.book.id}),
        )
        request.user = self.user
        request.current_book = self.book
        response = views.contact_views.CreateTagView.as_view()(
            request,
        )
        response.render()


class EditTagViewTests(TestCase):

    def setUp(self):
        self.book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(user=self.user,book=self.book)
        self.contact = factories.ContactFactory.create(book=self.book)
        self.tag = factories.TagFactory.create(tag='Test2', book=self.book)
        self.contact.tags.add(self.tag)
        self.request_factory = RequestFactory()

    def test_edit_tag_view_200(self):
        request = self.request_factory.get(
            reverse('tags-edit', kwargs={'pk': self.tag.pk, 'book': self.book.id}),
        )
        request.user = self.user
        request.current_book = self.book
        response = views.contact_views.EditTagView.as_view()(
            request,
            pk=self.tag.pk,
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_tag_view_renders(self):
        request = self.request_factory.get(
            reverse('tags-edit', kwargs={'pk': self.tag.pk, 'book': self.book.id}),
        )
        request.user = self.user
        request.current_book = self.book
        response = views.contact_views.EditTagView.as_view()(
            request,
            pk=self.tag.pk,
        )
        response.render()


class DeleteTagViewTests(TestCase):

    def setUp(self):
        self.book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(user=self.user,book=self.book)
        self.contact = factories.ContactFactory.create(book=self.book)
        self.tag = factories.TagFactory.create(tag='Test', book=self.book)
        self.contact.tags.add(self.tag)
        self.request_factory = RequestFactory()

    def test_delete_tag_view_200(self):
        request = self.request_factory.get(
            reverse('tags-delete', kwargs={'pk': self.tag.id, 'book': self.book.id}),
        )
        request.user = self.user
        request.current_book = self.book
        response = views.contact_views.DeleteTagView.as_view()(
            request,
            pk=self.tag.pk,
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_tag_view_renders(self):
        request = self.request_factory.get(
            reverse('tags-delete', kwargs={'pk': self.tag.id, 'book': self.book.id}),
        )
        request.user = self.user
        request.current_book = self.book
        response = views.contact_views.DeleteTagView.as_view()(
            request,
            pk=self.tag.pk,
        )
        response.render()



class CopyContactViewTests(TestCase):

    def setUp(self):
        self.book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(user=self.user,book=self.book)
        self.contact = factories.ContactFactory.create(book=self.book)
        request_factory = RequestFactory()
        self.request = request_factory.get(
            reverse('contacts-copy', kwargs={'pk': self.contact.id, 'book': self.book.id}),
        )
        self.request.current_book = self.book
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_copy_contact_view(self):
        contacts = models.Contact.objects.filter(book=self.book)
        self.assertEqual(1, len(contacts))
        self.request.user = self.user
        response = views.contact_views.CopyContactView.as_view()(
            self.request,
            pk=self.contact.pk,
        )
        self.assertEqual(response.status_code, 302)
        contacts = models.Contact.objects.filter(book=self.book)
        self.assertEqual(2, len(contacts))
        self.assertEqual(self.contact.name, contacts[1].name)

    def test_copy_contact_view_with_tags(self):
        self.tag = factories.TagFactory.create(tag='Test2', book=self.book)
        self.contact.tags.add(self.tag)
        self.request.user = self.user
        response = views.contact_views.CopyContactView.as_view()(
            self.request,
            pk=self.contact.pk,
        )
        self.assertEqual(response.status_code, 302)
        contacts = models.Contact.objects.filter(book=self.book)
        self.assertEqual(2, len(contacts))
        self.assertEqual(self.contact.tags.all()[0], contacts[1].tags.all()[0])


class BookSettingsViewTests(TestCase):

    def setUp(self):
        self.book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(user=self.user,book=self.book)
        request_factory = RequestFactory()
        self.request = request_factory.get(
            reverse('book_settings', kwargs={'book': self.book.id}),
        )
        self.request.current_book = self.book
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_book_settings_view_returns_and_renders(self):
        self.request.user = self.user
        response = views.book_views.BookSettingsView.as_view()(
            self.request,
            book=self.request.current_book,
        )
        self.assertEqual(response.status_code, 200)
        response.render()

