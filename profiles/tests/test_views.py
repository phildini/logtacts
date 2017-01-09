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


class ReviewUserViewTests(TestCase):

    def setUp(self):
        request_factory = RequestFactory()
        self.request = request_factory.get('/admin/dashboard/')

    def test_review_user_view_200(self):
        user = UserFactory.create()
        user.is_staff = True
        book = BookFactory.create()
        bookowner = BookOwnerFactory.create(user=user,book=book)
        self.request.user = user
        self.request.current_book = book
        response = ReviewUserView.as_view()(self.request)
        self.assertEqual(response.status_code, 200)

    def test_review_user_view_renders(self):
        user = UserFactory.create()
        user.is_staff = True
        book = BookFactory.create()
        bookowner = BookOwnerFactory.create(user=user,book=book)
        self.request.user = user
        self.request.current_book = book
        response = ReviewUserView.as_view()(self.request)
        response.render()

    def test_review_user_view_not_staff(self):
        user = UserFactory.create()
        book = BookFactory.create()
        bookowner = BookOwnerFactory.create(user=user,book=book)
        self.request.user = user
        self.request.current_book = book
        response = ReviewUserView.as_view()(self.request)
        self.assertEqual(response.status_code, 302)
