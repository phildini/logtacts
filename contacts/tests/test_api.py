from django.test import TestCase
from contacts import factories
from contacts.api import serializers


class TestSerializers(TestCase):

    def test_contact_serializer(self):
        contact = factories.ContactFactory.create()
        serialized_contact = serializers.ContactSerializer(contact)
        expected = {
            'company': None,
            'id': 1,
            'cell_phone': None,
            'notes': None,
            'email': 'philip+test@inkpebble.com',
            'home_phone': None,
            'name': 'Philip James',
            'tumblr': None,
            'website': None,
            'twitter':
            '@phildini',
            'address': None,
        }
        self.assertEqual(serialized_contact.data, expected)

    def test_tag_serializer(self):
        tag = factories.TagFactory.create(tag='Test')
        serialized_tag = serializers.TagSerializer(tag)
        expected = {
            'id': 1,
            'tag': 'Test',
            'color': None,
        }
        self.assertEqual(serialized_tag.data, expected)
