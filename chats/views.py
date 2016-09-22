import logging
import time
from string import ascii_lowercase

from twilio.twiml import Response

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseRedirect,
)
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet, SQ

from contacts.models import (
    Book,
    Contact,
    LogEntry,
)
from profiles.models import Profile

MET_PREFIXES = ('met', 'saw')
CACHE_TIMEOUT = 60
QUERY_ACCOUNT = 'query_account'
GET_EMAIL = 'get_email'
NEW_ACCOUNT = 'new_account'


@csrf_exempt
def sms(request):
    if request.method == 'GET':
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        overall_start = time.time()
        cache_key = request.POST.get('From')
        co_number = request.POST.get('To')
        message = request.POST.get('Body').strip()
        if not cache_key:
            raise Http404()
        flow_state = cache.get(cache_key)
        if flow_state:
            if message.lower() == 'done':
                cache.delete(cache_key)
                return help_message()
            if flow_state == QUERY_ACCOUNT:
                if message.lower() in ('yes', 'yep'):
                    cache.set(cache_key, GET_EMAIL, CACHE_TIMEOUT)
                    return create_message(
                        "Ok, what's the email address on your account?",
                        to=cache_key, sender=co_number,
                    )
                else:
                    cache.delete(cache_key)
                    return create_message(
                        "Ok! Please go to https://www.contactotter.com to create an account.",
                        to=cache_key, sender=co_number,
                    )
            if flow_state == GET_EMAIL:
                try:
                    # TODO: Send a confirmation email for connecting phone
                    user = User.objects.get(email=message.lower())
                    profile, _ = Profile.objects.get_or_create(user=user)
                    profile.phone_number = cache_key
                    profile.save()
                    cache.delete(cache_key)
                    return create_message(
                        "Ok! Your phone is connected to your account.",
                        to=cache_key, sender=co_number,
                    )
                except User.DoesNotExist:
                    cache.delete(cache_key)
                    return create_message(
                        "We couldn't find an account for that email. Please go to https://www.contactotter.com to create one",
                        to=cache_key, sender=co_number,
                    )
        user, book = get_user_objects_from_message(request.POST)
        if not user or not book:
            cache.set(cache_key, QUERY_ACCOUNT, CACHE_TIMEOUT)
            return create_message(
                "Hmm... I can't find an account with this number. Do you have a ContactOtter account?",
                to=cache_key, sender=co_number,
            )

        if flow_state:
            if flow_state.startswith('log'):
                name = ':'.join(flow_state.split(':')[1:])
                contacts = SearchQuerySet().filter(book=book.id).filter(
                    SQ(name=AutoQuery(name)) | SQ(content=AutoQuery(name))
                )
                if len(message) == 1 and len(contacts) > 0:
                    index = ascii_lowercase.index(message.lower())
                    contact = contacts[index].object
                    cache.delete(cache_key)
                    return log_contact(contact, user)
                cache.delete(cache_key)
                return create_message(
                    "Sorry, I didn't understand that.",
                    to=cache_key, sender=co_number,
                )
            if flow_state.startswith('find'):
                name = ':'.join(flow_state.split(':')[1:])
                contacts = SearchQuerySet().filter(book=book.id).filter(
                    SQ(name=AutoQuery(name)) | SQ(content=AutoQuery(name))
                )
                if len(message) == 1 and len(contacts) > 0:
                    index = ascii_lowercase.index(message.lower())
                    contact = contacts[index].object
                    cache.delete(cache_key)
                    return create_message(
                        get_contact_string(contact), to=cache_key, sender=co_number,
                    )
                cache.delete(cache_key)
                return create_message(
                    "Sorry, I didn't understand that.",
                    to=cache_key, sender=co_number,
                )


        tokens = message.split(' ')
        if len(tokens) < 2:
            return help_message()

        search_start = time.time()
        if tokens[0].lower() in MET_PREFIXES:
            if tokens[1].lower() == 'with':
                del tokens[1]
            name = ' '.join(tokens[1:])
            contacts = SearchQuerySet().filter(book=book.id).filter(
                SQ(name=AutoQuery(name)) | SQ(content=AutoQuery(name))
            )
            if len(contacts) > 1:
                cache.set(cache_key, "log:{}".format(name), CACHE_TIMEOUT)
                response_string = "Which {} did you mean?\n".format(name)
                response_string += get_string_from_search_contacts(contacts)
                response_string += "(DONE to exit)"
                return create_message(
                    response_string, to=cache_key, sender=co_number,
                )
            if len(contacts) == 1:
                contact = contacts[0].object
            else:
                contact = Contact.objects.create(
                    book=book,
                    name=name,
                )

            cache.delete(cache_key)
            return log_contact(contact, user)

        if tokens[0].lower() == 'find':
            name = ' '.join(tokens[1:])
            contacts = SearchQuerySet().filter(book=book.id).filter(
                SQ(name=AutoQuery(name)) | SQ(content=AutoQuery(name))
            )
            if len(contacts) == 0:
                return create_message(
                    "Hmm... I didn't find any contacts.",
                    to=cache_key, sender=co_number,
                )
            if len(contacts) == 1:
                return create_message(
                    get_contact_string(contacts[0].object),
                    to=cache_key, sender=co_number,
                )
            response_string = get_string_from_search_contacts(contacts)
            if len(contacts) > 3:
                response_string += "More: https://{}/search/?q={}".format(
                    Site.objects.get_current().domain,
                    name,
                )
            cache.set(cache_key, "find:{}".format(name), CACHE_TIMEOUT)
            return create_message(
                "Here's what I found for {}:\n{}".format(name, response_string),
                to=cache_key, sender=co_number,
            )
        return help_message()


def create_message(message, to, sender):
    r = Response()
    r.message(message, to=to, sender=sender)
    return HttpResponse(r.toxml(), content_type='text/xml')


def log_contact(contact, user):
    time =timezone.now()
    LogEntry.objects.create(
        contact=contact,
        logged_by=user,
        time=timezone.now(),
        kind='in person'
    )
    contact.last_contact = time
    contact.save()
    r = Response()
    r.message(
        "Updated {} ({})".format(contact.name, contact.get_complete_url())
    )
    return HttpResponse(r.toxml(), content_type='text/xml')


def get_string_from_search_contacts(contacts):
    response_string = ""
    for index, contact in enumerate(contacts[:3]):
        contact = contact.object
        letter = ascii_lowercase[index]
        response_string += "{}: {} ({})\n".format(
            letter.upper(), contact.name, contact.get_complete_url(),
        )
    return response_string


def get_contact_string(contact):
    response_string = "{}\n".format(contact.name)
    if contact.preferred_phone:
        response_string += "{}\n".format(contact.preferred_phone)
    if contact.preferred_email:
        response_string += "{}\n".format(contact.preferred_email)
    if contact.preferred_address:
        response_string += "{}\n".format(contact.preferred_address)
    response_string += "{}\n".format(contact.get_complete_url())
    return response_string


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
