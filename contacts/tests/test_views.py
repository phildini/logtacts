from django.core.urlresolvers import reverse
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


class TaggedContactListViewTests(TestCase):

    def setUp(self):
        book = factories.BookFactory.create()
        user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(user=user,book=book)
        tag = factories.TagFactory()
        contact = factories.ContactFactory.create(book=book, tags=[tag])
        request_factory = RequestFactory()
        request = request_factory.get(reverse('contacts-tagged', kwargs={'pk': tag.pk}))
        request.user = UserFactory.create()
        self.response = views.contact_views.TaggedContactListView.as_view()(request)

    def test_contact_list_view_renders_no_philip(self):
        self.response.render()  # crashes: DoesNotExist: Tag matching query does not exist.


class ContactViewTests(TestCase):
    def setUp(self):
        book = factories.BookFactory.create()
        user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(user=user,book=book)
        contact = factories.ContactFactory.create(book=book)
        request_factory = RequestFactory()
        request = request_factory.get(contact.get_absolute_url())
        request.user = UserFactory.create()
        self.response = views.contact_views.ContactListView.as_view()(request)

    def test_contact_detail_view_response_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_contact_detail_view_renders(self):
        self.response.render()
