from django.test import TestCase
from profiles import factories


class ProfileModelTests(TestCase):

    def setUp(self):
        self.profile = factories.ProfileFactory()

    def test_profile_name(self):
        self.assertEqual(
            "{}'s profile".format(self.profile.user),
            str(self.profile),
        )