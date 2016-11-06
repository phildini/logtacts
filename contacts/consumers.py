import datetime
import logging

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

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
        success = True
        if success:
            cache.delete("{}::google-import".format(user))
            try:
                context = {
                    'domain': Site.objects.get_current().domain,
                }
                txt = get_template('email/google_import_done.txt').render(context)
                html = get_template('email/google_import_done.html').render(context)
                message = EmailMultiAlternatives(
                    subject='Contact import finished!',
                    body=txt,
                    from_email="ContactOtter <import@contactotter.com>",
                    to=[user.email],
                    headers={
                        'Reply-To': "ContactOtter <support@contactotter.com>",
                    },
                )
                message.attach_alternative(html, "text/html")
                message.send()
            except:
                logger.error("Error sending import success email", exc_info=True)
    except:
        cache.set("{}::google-import".format(user), "error", 86400)