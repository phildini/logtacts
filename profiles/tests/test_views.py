from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from common.factories import UserFactory
from contacts.factories import BookFactory, BookOwnerFactory

from profiles.views import (
    ProfileView,
    ReviewUserView,
)


class ProfileViewTests(TestCase):

    def setUp(self):
        book = BookFactory.create()
        self.user = UserFactory.create(username='phildini')
        bookowner = BookOwnerFactory.create(user=self.user,book=book)
        request_factory = RequestFactory()
        request = request_factory.get(reverse('profile'))
        request.user = self.user
        request.current_book = book
        self.response = ProfileView.as_view()(request)

    def test_profile_view_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_profile_view_renders(self):
        self.response.render()