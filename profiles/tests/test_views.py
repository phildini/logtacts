from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from utils.factories import UserFactory

from profiles.views import (
    ProfileView,
    ReviewUserView,
)


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


class ReviewUserViewTests(TestCase):

    def setUp(self):
        request_factory = RequestFactory()
        self.request = request_factory.get('/admin/dashboard/')

    def test_review_user_view_200(self):
        user = UserFactory.create()
        user.is_staff = True
        self.request.user = user
        response = ReviewUserView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_review_user_view_200(self):
        user = UserFactory.create()
        user.is_staff = True
        self.request.user = user
        response = ReviewUserView.as_view()(self.request)
        response.render()

    def test_review_user_view_not_staff(self):
        user = UserFactory.create()
        self.request.user = user
        response = ReviewUserView.as_view()(self.request)
        self.assertEqual(response.status_code, 302)
