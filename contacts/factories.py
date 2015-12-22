import factory

from django.utils import timezone
from utils.factories import UserFactory
from . import models


class ContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Contact


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Book


class BookOwnerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.BookOwner

    user = factory.SubFactory(UserFactory)
    book = factory.SubFactory(BookFactory)


class LogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.LogEntry

    contact = factory.SubFactory(ContactFactory)
    created = timezone.now()


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Tag