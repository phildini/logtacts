import factory

from django.utils import timezone
from common.factories import UserFactory
from . import models


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Profile

    user = factory.SubFactory(UserFactory)