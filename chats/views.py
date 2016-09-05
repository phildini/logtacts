from twilio.twiml import Response

from django.contrib.sites.models import Site
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
)
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet

from contacts.models import (
    Book,
    Contact,
    LogEntry,
)
from profiles.models import Profile

MET_PREFIXES = ('met', 'saw')


@csrf_exempt
def sms(request):
    if request.method == 'GET':
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        import pdb; pdb.set_trace()
        user, book = get_user_objects_from_message(request.POST)
        if not user or not book:
            r = Response()
            r.message("Hmm... It looks like your ContactOtter account isn't set up yet. Go to https://www.contactotter.com to get things ready!")
            return HttpResponse(r.toxml(), content_type='text/xml')

        message = request.POST.get('Body').strip()

        tokens = message.split(' ')
        if len(tokens) < 2:
            return help_message()

        if tokens[0].lower() in MET_PREFIXES:
            if tokens[1].lower() == 'with':
                del tokens[1]
            name = ' '.join(tokens[1:])
            contacts = SearchQuerySet().filter(
                book=book.id,
                content=AutoQuery(name),
            )

            if len(contacts) > 0:
                contact = contacts[0].object
            else:
                contact = Contact.objects.create(
                    book=book,
                    name=name,
                )

            LogEntry.objects.create(
                contact=contact,
                logged_by=user,
                time=timezone.now(),
                kind='in person'
            )

            r.message(
                "Updated {} ({})".format(contact.name, contact.get_complete_url())
            )
            return HttpResponse(r.toxml(), content_type='text/xml')

        if tokens[0].lower() == 'find':
            name = ' '.join(tokens[1:])
            contacts = SearchQuerySet().filter(
                book=book.id,
                content=AutoQuery(name),
            )
            response_string = ""
            for contact in contacts[:4]:
                contact = contact.object
                response_string += "{} ({})\n".format(
                    contact.name, contact.get_complete_url()
                )
            if len(contacts) > 4:
                response_string += "More: https://{}/search/?q={}".format(
                    Site.objects.get_current().domain,
                    name,
                )
            r.message("Here's what I found for {}:\n{}".format(name, response_string))
            return HttpResponse(r.toxml(), content_type='text/xml')

        return help_message()


def get_user_objects_from_message(post_data):
    sender = post_data.get('From')
    try:
        profile = Profile.objects.get(phone_number=sender)
        user = profile.user
    except Profile.DoesNotExist:
        return None, None

    try:
        book = Book.objects.get_for_user(user)
    except Book.DoesNotExist:
        return None, None
    return user, book


def help_message():
    r = Response()
    message_string = (
        "Hello! I understand:\n"
        "'Add Jane Doe' to add Jane Doe as a contact\n"
        "'Met Jane Doe' to log that you met Jane Doe\n"
        "'Find Jane Doe' to search for Jane in your contacts"
    )
    r.message(message_string)
    return HttpResponse(r.toxml(), content_type='text/xml')

