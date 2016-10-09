import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import contacts as contact_settings
from contacts.models import (
    Book,
    BookOwner,
    Contact,
    ContactField,
    Tag,
    LogEntry,
)


fake = Faker()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--book',
            type=int,
            dest='book',
            default=1,
            help='Book id to add generated contacts to',
        )

        parser.add_argument(
            '--reset',
            action='store_true',
            dest='reset',
            default=False,
            help='Flag to reset the book at specified book id',
        )

    def handle(self, *args, **options):
        book = Book.objects.get(id=options['book'])
        user = BookOwner.objects.filter(book=book)[0].user
        tags = []
        if options['reset']:
            Contact.objects.filter(book=book).delete()
            Tag.objects.filter(book=book).delete()
        for n in range(10):
            tags.append(Tag.objects.create(
                book=book,
                tag=fake.word(),
                color=fake.safe_hex_color(),
            ))
        for n in range(40):
            tag1 = random.choice(tags)
            tag2 = random.choice(tags)
            contact = Contact.objects.create(
                book=book,
                name=fake.name(),
            )
            contact.tags.add(tag1, tag2)
            contact.save()

            ContactField.objects.create(
                contact=contact,
                kind=contact_settings.FIELD_TYPE_ADDRESS,
                label="Address",
                value=fake.address(),
            )
            ContactField.objects.create(
                contact=contact,
                kind=contact_settings.FIELD_TYPE_TEXT,
                label="Company",
                value=fake.company(),
            )
            ContactField.objects.create(
                contact=contact,
                kind=contact_settings.FIELD_TYPE_EMAIL,
                label="Email",
                value=fake.email(),
            )
            ContactField.objects.create(
                contact=contact,
                kind=contact_settings.FIELD_TYPE_TEXT,
                label="Job",
                value=fake.job(),
            )
            ContactField.objects.create(
                contact=contact,
                kind=contact_settings.FIELD_TYPE_PHONE,
                label="Phone",
                value=fake.phone_number(),
            )
            ContactField.objects.create(
                contact=contact,
                kind=contact_settings.FIELD_TYPE_URL,
                label="Website",
                value=fake.url(),
            )
            for n in range(5):
                log = LogEntry.objects.create(
                    contact=contact,
                    time=fake.date_time_this_year(
                        tzinfo=timezone.get_current_timezone(),
                    ),
                    kind=random.choice(LogEntry.KIND_CHOICES),
                    notes=fake.text(max_nb_chars=100),
                    link=fake.url(),
                    logged_by=user,
                )
                contact.update_last_contact_from_log(log)
