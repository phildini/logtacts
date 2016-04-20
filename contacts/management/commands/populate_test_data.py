from django.core.management.base import BaseCommand

from contacts.models import Book, Contact, ContactField

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        book = Book.objects.get(id=1)
        for n in range(40):
            contact = Contact.objects.create(
                book=book,
                name='Test {}'.format(n),
            )
            for m in range(10):
                ContactField.objects.create(
                    contact=contact,
                    kind='email',
                    label='Test {}'.format(m),
                    value='pjj+{}@pjj.pjj'.format(m),
                )
