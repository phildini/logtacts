from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.http.response import Http404
from django.test import TestCase
from django.test.client import RequestFactory

from utils.factories import UserFactory

from contacts import factories
from contacts import views


class ContactListViewTests(TestCase):

    def setUp(self):
        request_factory = RequestFactory()
        request = request_factory.get(reverse('contacts-list'))
        request.user = UserFactory.create()
        self.response = views.contact_views.ContactListView.as_view()(request)

    def test_contact_list_view_response_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_contact_list_view_renders(self):
        self.response.render()


class ContactViewTests(TestCase):
    def setUp(self):
        book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(user=self.user,book=book)
        self.contact = factories.ContactFactory.create(book=book)
        request_factory = RequestFactory()
        self.request = request_factory.get(self.contact.get_absolute_url())

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


class LogViewTests(TestCase):

    def setUp(self):
        book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(user=self.user,book=book)
        self.contact = factories.ContactFactory.create(book=book)
        self.log = factories.LogFactory.create(contact=self.contact)
        self.request_factory = RequestFactory()

    def test_log_edit_view_200_if_right_user(self):
        self.request = self.request_factory.get(
            reverse('log-edit', kwargs={'pk': self.log.id})
        )
        self.request.user = self.user
        response = views.log_views.EditLogView.as_view()(
            self.request,
            pk=self.log.pk,
        )
        self.assertEqual(response.status_code, 200)

    def test_log_edit_view_401_if_right_user(self):
        self.request = self.request_factory.get(
            reverse('log-edit', kwargs={'pk': self.log.id})
        )
        self.request.user = UserFactory.create()
        with self.assertRaises(PermissionDenied):
            views.log_views.EditLogView.as_view()(
                self.request,
                pk=self.log.pk,
            )

    def test_log_edit_view_renders(self):
        self.request = self.request_factory.get(
            reverse('log-edit', kwargs={'pk': self.log.id})
        )
        self.request.user = self.user
        response = views.log_views.EditLogView.as_view()(
            self.request,
            pk=self.log.pk,
        )
        response.render()

    def test_log_delete_view_200_if_right_user(self):
        self.request = self.request_factory.get(
            reverse('log-delete', kwargs={'pk': self.log.id})
        )
        self.request.user = self.user
        response = views.log_views.DeleteLogView.as_view()(
            self.request,
            pk=self.log.pk,
        )
        self.assertEqual(response.status_code, 200)

    def test_log_delete_view_401_if_wrong_user(self):
        self.request = self.request_factory.get(
            reverse('log-delete', kwargs={'pk': self.log.id})
        )
        self.request.user = UserFactory.create()
        with self.assertRaises(PermissionDenied):
            views.log_views.DeleteLogView.as_view()(
                self.request,
                pk=self.log.pk,
            )

    def test_log_delete_view_renders(self):
        self.request = self.request_factory.get(
            reverse('log-delete', kwargs={'pk': self.log.id})
        )
        self.request.user = self.user
        response = views.log_views.DeleteLogView.as_view()(
            self.request,
            pk=self.log.pk,
        )
        response.render()


class TagViewTests(TestCase):

    def setUp(self):
        book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(user=self.user,book=book)
        self.contact = factories.ContactFactory.create(book=book)
        self.tag = factories.TagFactory.create(tag='Test', book=book)
        self.contact.tags.add(self.tag)
        self.request_factory = RequestFactory()

    def test_tagged_list_view_200(self):
        request = self.request_factory.get(
            reverse('contacts-tagged', kwargs={'pk': self.tag.id}),
        )
        request.user = self.user
        response = views.contact_views.TaggedContactListView.as_view()(
            request,
            pk=self.tag.pk,
        )
        self.assertEqual(response.status_code, 200)

    def test_tagged_list_view_401_if_wrong_user(self):
        request = self.request_factory.get(
            reverse('contacts-tagged', kwargs={'pk': self.tag.id})
        )
        request.user = UserFactory.create()
        with self.assertRaises(Http404):
            views.contact_views.TaggedContactListView.as_view()(
                request,
                pk=self.tag.pk,
            )

    def test_tagged_list_view_renders(self):
        request = self.request_factory.get(
            reverse('contacts-tagged', kwargs={'pk': self.tag.id}),
        )
        request.user = self.user
        response = views.contact_views.TaggedContactListView.as_view()(
            request,
            pk=self.tag.pk,
        )
        response.render()