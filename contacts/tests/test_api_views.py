from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from utils.factories import UserFactory
from contacts import factories
from contacts.api import serializers
from contacts.api import views
from contacts.models import LogEntry


class ContactSearchAPIViewTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(
            book=self.book,
            user=self.user,
        )

    def test_contact_search_no_search_string(self):
        request = self.factory.get('/api/search/', format='json')
        force_authenticate(request, user=self.user)
        response = views.ContactSearchAPIView.as_view()(request)
        response.render()
        self.assertEqual(response.status_code, 400)

    def test_contact_search_no_book(self):
        request = self.factory.get('/api/search/?q=phil', format='json')
        user = UserFactory.create(username="asheesh")
        force_authenticate(request, user=user)
        response = views.ContactSearchAPIView.as_view()(request)
        response.render()
        self.assertEqual(response.status_code, 400)



class TagListAPIViewTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(
            book=self.book,
            user=self.user,
        )

    def test_tag_list_view(self):
        tag = factories.TagFactory.create(book=self.book)
        request = self.factory.get('/api/tags/', format='json')
        force_authenticate(request, user=self.user)
        response = views.TagListCreateAPIView.as_view()(request)
        response.render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_tag_list_view_wrong_user_for_book(self):
        tag = factories.TagFactory.create(book=self.book)
        request = self.factory.get('/api/tags/', format='json')
        user = UserFactory.create(username='asheesh')
        force_authenticate(request, user=user)
        response = views.TagListCreateAPIView.as_view()(request)
        response.render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_tag_create_view(self):
        request = self.factory.post(
            '/api/tags/',
            {'tag': 'Test tag', 'book': str(self.book.id)},
            format='json',
        )
        force_authenticate(request, user=self.user)
        response = views.TagListCreateAPIView.as_view()(request)
        response.render()
        self.assertEqual(response.status_code, 201)

    def test_tag_create_view_wrong_book_for_user(self):
        request = self.factory.post(
            '/api/tags/',
            {'tag': 'Test tag', 'book': str(self.book.id)},
            format='json',
        )
        user = UserFactory.create(username='nicholle')
        force_authenticate(request, user=user)
        response = views.TagListCreateAPIView.as_view()(request)
        response.render()
        self.assertEqual(response.status_code, 401)


class ContactListCreateAPIViewTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(
            book=self.book,
            user=self.user,
        )

    def test_contact_list_view(self):
        contact = factories.ContactFactory.create(book=self.book)
        request = self.factory.get('/api/contacts/', format='json')
        force_authenticate(request, user=self.user)
        response = views.ContactListCreateAPIView.as_view()(request)
        response.render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_contact_list_view_wrong_user_for_book(self):
        contact = factories.ContactFactory.create(book=self.book)
        request = self.factory.get('/api/contacts/', format='json')
        user = UserFactory.create(username='asheesh')
        force_authenticate(request, user=user)
        response = views.ContactListCreateAPIView.as_view()(request)
        response.render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_contact_create_view(self):
        request = self.factory.post(
            '/api/contacts/',
            {'name': 'Philip', 'book': str(self.book.id)},
            format='json',
        )
        force_authenticate(request, user=self.user)
        response = views.ContactListCreateAPIView.as_view()(request)
        response.render()
        self.assertEqual(response.status_code, 201)

    def test_contact_create_view_wrong_book_for_user(self):
        request = self.factory.post(
            '/api/contacts/',
            {'name': 'Philip', 'book': str(self.book.id)},
            format='json',
        )
        user = UserFactory.create(username='asheesh')
        force_authenticate(request, user=user)
        response = views.ContactListCreateAPIView.as_view()(request)
        response.render()
        self.assertEqual(response.status_code, 401)


class ContactDetailEditAPIViewTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(
            book=self.book,
            user=self.user,
        )

    def test_contact_detail_edit_view_200(self):
        contact = factories.ContactFactory.create(book=self.book)
        request = self.factory.get(
            '/api/contacts/{}'.format(contact.pk),
            format='json',
        )
        force_authenticate(request, user=self.user)
        response = views.ContactDetailEditAPIView.as_view()(
            request,
            pk=contact.id,
        )
        response.render()
        self.assertEqual(response.status_code, 200)

    def test_contact_detail_successful_edits(self):
        contact = factories.ContactFactory.create(book=self.book)
        request = self.factory.put(
            '/api/contacts/{}'.format(contact.pk),
            {'name': 'Asheesh'},
            format='json',
        )
        force_authenticate(request, user=self.user)
        response = views.ContactDetailEditAPIView.as_view()(
            request,
            pk=contact.id,
        )
        response.render()
        self.assertEqual(response.status_code, 200)

    def test_contact_detail_edit_creates_log(self):
        contact = factories.ContactFactory.create(book=self.book)
        request = self.factory.put(
            '/api/contacts/{}'.format(contact.pk),
            {'name': 'Asheesh'},
            format='json',
        )
        force_authenticate(request, user=self.user)
        response = views.ContactDetailEditAPIView.as_view()(
            request,
            pk=contact.id,
        )
        response.render()
        new_log = LogEntry.objects.get(
            logged_by=self.user, contact=contact, kind='edit',
        )

    def test_contact_detail_raises_404_if_wrong_user(self):
        contact = factories.ContactFactory.create(book=self.book)
        request = self.factory.get(
            '/api/contacts/{}'.format(contact.pk),
            format='json',
        )
        user = UserFactory.create(username="asheesh")
        force_authenticate(request, user=user)
        response = views.ContactDetailEditAPIView.as_view()(
            request,
            pk=contact.id,
        )
        response.render()
        self.assertEqual(response.status_code, 404)


class LogListCreateAPIViewTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(
            book=self.book,
            user=self.user,
        )
        self.contact = factories.ContactFactory(book=self.book)
        self.url = '/api/contacts/{}/tags/'.format(self.contact.id)
        self.log = factories.LogFactory.create(contact=self.contact)

    def test_log_list_view(self):
        request = self.factory.get(self.url, format='json')
        force_authenticate(request, user=self.user)
        response = views.LogListCreateAPIView.as_view()(
            request,
            pk=self.contact.id,
        )
        response.render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_log_list_view_wrong_user_for_book(self):
        request = self.factory.get(self.url, format='json')
        user = UserFactory.create(username='asheesh')
        force_authenticate(request, user=user)
        response = views.LogListCreateAPIView.as_view()(
            request,
            pk=self.contact.id,
        )
        response.render()
        self.assertEqual(response.status_code, 404)

    def test_log_create_view(self):
        request = self.factory.post(
            self.url,
            {'contact': str(self.contact.id)},
            format='json',
        )
        force_authenticate(request, user=self.user)
        response = views.LogListCreateAPIView.as_view()(
            request,
            pk=self.contact.id,
        )
        response.render()
        self.assertEqual(response.status_code, 201)

    def test_log_create_view_wrong_book_for_user(self):
        request = self.factory.post(
            '/api/contacts/',
            {'contact': str(self.contact.id)},
            format='json',
        )
        user = UserFactory.create(username='asheesh')
        force_authenticate(request, user=user)
        response = views.LogListCreateAPIView.as_view()(
            request,
            pk=self.contact.id,
        )
        response.render()
        self.assertEqual(response.status_code, 404)
