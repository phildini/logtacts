from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Book, BookOwner, LogEntry


@receiver(post_save, sender=User)
def create_book_for_sandstorm_user(sender, instance=None, created=False, **kwargs):
    if not kwargs.get('raw') and instance and created:
        try:
            BookOwner.objects.get(user=instance)
        except BookOwner.DoesNotExist:
            if settings.SANDSTORM:
                books = Book.objects.all()
                if len(books) > 0:
                    book = Book.objects.all()[0]
                else:
                    book = Book.objects.create(name="{}'s Contacts".format(instance))
                BookOwner.objects.create(user=instance, book=book)
