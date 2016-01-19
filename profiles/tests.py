from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from utils.factories import UserFactory

from profiles.views import ProfileView


class ProfileViewTests(TestCase):

    def setUp(self):
        request_factory = RequestFactory()
        request = request_factory.get(reverse('profile'))
        request.user = UserFactory.create()
        self.response = ProfileView.as_view()(request)

    def test_profile_view_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_profile_view_renders(self):
        self.response.render()
