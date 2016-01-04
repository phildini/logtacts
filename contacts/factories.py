import factory

from django.utils import timezone
from utils.factories import UserFactory
from . import models


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Book


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Tag

    tag = "person"


class ContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Contact

    name = "Philip James"
    book = factory.SubFactory(BookFactory)
    email = "philip+test@inkpebble.com"
    twitter = "@phildini"
    tags = factory.Sequence(factory.SubFactory(TagFactory))

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)


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
