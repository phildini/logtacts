import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from profiles.models import Profile

logger = logging.getLogger('scripts')


class Command(BaseCommand):
    help = "add Profiles for users without them"

    def handle(self, *args, **kwargs):
        users_to_update = User.objects.filter(profile__isnull=True)
        for user in users_to_update:
            Profile.objects.create(user=user)