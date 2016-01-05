from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from utils.factories import UserFactory
from contacts import factories
from contacts.api import serializers
from contacts.api import views


class TestSerializers(TestCase):

    def test_contact_serializer(self):
        contact = factories.ContactFactory.create()
        serialized_contact = serializers.ContactSerializer(contact)
        expected = {
            'company': None,
            'address': None,
            'website': None,
            'home_phone': None,
            'notes': None,
            'name': 'Philip James',
            'tumblr': None,
            'cell_phone': None,
            'twitter': '@phildini',
            'id': 1,
            'book': 1,
            'tags': [],
            'email': 'philip+test@inkpebble.com',
        }
        self.assertEqual(serialized_contact.data, expected)

    def test_contact_serializer_with_tags(self):
        contact = factories.ContactFactory.create()
        tag = factories.TagFactory.create(tag='test')
        contact.tags.add(tag)
        serialized_contact = serializers.ContactSerializer(contact)
        expected = {
            'id': 1, 'home_phone': None,
            'book': 1,
            'notes': None,
            'tags': [1],
            'tumblr': None,
            'website': None,
            'twitter': '@phildini',
            'cell_phone': None,
            'name': 'Philip James',
            'address': None,
            'company': None,
            'email': 'philip+test@inkpebble.com',
        }
        self.assertEqual(serialized_contact.data, expected)

    def test_tag_serializer(self):
        tag = factories.TagFactory.create(tag='Test')
        serialized_tag = serializers.TagSerializer(tag)
        expected = {
            'id': 1,
            'tag': 'Test',
            'book': None,
            'color': None,
        }
        self.assertEqual(serialized_tag.data, expected)

    def test_log_serializer(self):
        log = factories.LogFactory.create()
        serialized_log = serializers.LogSerializer(log)
        expected = {
            'notes': '',
            'id': 1,
            'contact': 1,
            'location': None,
            'link': None,
            'time': None,
            'kind': None,
        }
        self.assertEqual(serialized_log.data, expected)


class TestAPIViews(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.book = factories.BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = factories.BookOwnerFactory.create(book=self.book,user=self.user)

    def test_tag_create_view(self):
        request = self.factory.post('/api/tags/', {'tag': 'Test tag', 'book': str(self.book.id)}, format='json')
        force_authenticate(request, user=self.user)
        view = views.TagListCreateAPIView.as_view()
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, 201)

    def test_tag_create_view_bad_book(self):
        request = self.factory.post('/api/tags/', {'tag': 'Test tag', 'book': str(self.book.id)}, format='json')
        user = UserFactory.create(username='nicholle')
        force_authenticate(request, user=user)
        view = views.TagListCreateAPIView.as_view()
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, 401)

