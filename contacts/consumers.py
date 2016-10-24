import datetime
import logging

from django.contrib.auth.models import User
from django.core.cache import cache

from contacts.models import Book
from .utils import pull_google_contacts

logger = logging.getLogger("sentry")


def import_google_contacts(message):
    try:
        user = User.objects.get(id=message.get('user_id'))
        book = Book.objects.get(bookowner__user=user, id=message.get('book_id'))
    except Book.DoesNotExist:
        logger.error("Bad book passed to google import job", exc_info=True)
        return
    except User.DoesNotExist:
        logger.error("Bad user passed to google import job", exc_info=True)
        return
    try:
        success = pull_google_contacts(user=user, book=book)
        if success:
            cache.delete("{}::google-import".format(user))
    except:
        cache.set("{}::google-import".format(user), "error", 86400)