from django.core.cache import cache
from django.test import TestCase
from unittest.mock import MagicMock, patch

from contacts import factories as contact_factories
from profiles import factories as profile_factories


from .views import nexmo_send, handle, help_message


class ChatFlowHandlerTests(TestCase):

    def setUp(self):
        self.sender = '18318675309'
        self.receiver = '15105555555'
        cache.delete(self.sender)
        self.book = contact_factories.BookFactory.create()

    def test_start_unknown_number(self):
        with patch('chats.views.nexmo_send', return_value=None) as send_function:
            handle(self.sender, self.receiver, 'Hello')
            send_function.assert_called_with(self.receiver, self.sender, "Hmm... I can't find an account with this number. Do you have a ContactOtter account?")

    def test_start_known_number(self):
        profile = profile_factories.ProfileFactory.create(phone_number='+' + self.sender)
        contact_factories.BookOwnerFactory.create(user=profile.user, book=self.book)
        with patch('chats.views.nexmo_send', return_value=None) as send_function:
            handle(self.sender, self.receiver, 'Hello')
            send_function.assert_called_with(self.receiver, self.sender, help_message())
