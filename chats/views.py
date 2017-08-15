import logging
import time
import nexmo
from string import ascii_lowercase

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseRedirect,
)
from django.utils import timezone
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

client = nexmo.Client(key=settings.NEXMO_KEY, secret=settings.NEXMO_SECRET)

def nexmo_send(sender, receiver, message):
    client.send_message({
        'from': sender,
        'to': receiver,
        'text': message,
    })
    return HttpResponse()

def handle(sender, receiver, message):
    overall_start = time.time()
    flow_state = cache.get(sender)
    if flow_state:
        if message == 'done':
            cache.delete(sender)
            return nexmo_send(receiver, sender, help_message())
        if flow_state == QUERY_ACCOUNT:
            if message in ('yes', 'yep'):
                cache.set(sender, GET_EMAIL, CACHE_TIMEOUT)
                return nexmo_send(receiver, sender, "Ok, what's the email address on your account?")
            else:
                cache.delete(sender)
                return nexmo_send(receiver, sender, "Ok! Please go to https://www.contactotter.com to create an account.")
    user, book = get_user_objects_from_message(sender)
    if not user or not book:
        cache.set(sender, QUERY_ACCOUNT, CACHE_TIMEOUT)
        return nexmo_send(receiver, sender, "Hmm... I can't find an account with this number. Do you have a ContactOtter account?")
    if flow_state:
        if flow_state.startswith('log'):
            name = ':'.join(flow_state.split(':')[1:])
            contacts = SearchQuerySet().filter(book=book.id).filter(
                SQ(name=AutoQuery(name)) | SQ(content=AutoQuery(name))
            )
            if len(message) == 1 and len(contacts) > 0:
                index = ascii_lowercase.index(message)
                contact = contacts[index].object
                cache.delete(sender)
                log_contact(contact, user)
                return nexmo_send(receiver, sender, "Updated {} ({})".format(contact.name, contact.get_complete_url()))
            cache.delete(sender)
            return nexmo_send(receiver, sender, "Sorry, I didn't understand that.")
        if flow_state.startswith('find'):
            name = ':'.join(flow_state.split(':')[1:])
            contacts = SearchQuerySet().filter(book=book.id).filter(
                SQ(name=AutoQuery(name)) | SQ(content=AutoQuery(name))
            )
            if len(message) == 1 and len(contacts) > 0:
                index = ascii_lowercase.index(message)
                contact = contacts[index].object
                cache.delete(sender)
                return nexmo_send(receiver, sender, get_contact_string(contact))
            cache.delete(sender)
            return nexmo_send(receiver, sender, "Sorry, I didn't understand that.")
    tokens = message.split(' ')
    if len(tokens) < 2:
        return nexmo_send(receiver, sender, help_message())
    search_start = time.time()
    if tokens[0].lower() in MET_PREFIXES:
        if tokens[1].lower() == 'with':
            del tokens[1]
        name = ' '.join(tokens[1:])
        contacts = SearchQuerySet().filter(book=book.id).filter(
            SQ(name=AutoQuery(name)) | SQ(content=AutoQuery(name))
        )
        if len(contacts) > 1:
            cache.set(sender, "log:{}".format(name), CACHE_TIMEOUT)
            response_string = "Which {} did you mean?\n".format(name)
            response_string += get_string_from_search_contacts(contacts)
            response_string += "(DONE to exit)"
            return nexmo_send(receiver, sender, response_string)
        if len(contacts) == 1:
            contact = contacts[0].object
        else:
            contact = Contact.objects.create(
                book=book,
                name=name,
            )
        cache.delete(sender)
        log_contact(contact, user)
        return nexmo_send(receiver, sender, "Updated {} ({})".format(contact.name, contact.get_complete_url()))
    if tokens[0].lower() == 'find':
        name = ' '.join(tokens[1:])
        contacts = SearchQuerySet().filter(book=book.id).filter(
            SQ(name=AutoQuery(name)) | SQ(content=AutoQuery(name))
        )
        if len(contacts) == 0:
            return nexmo_send(receiver, sender, "Hmm... I didn't find any contacts.")
        if len(contacts) == 1:
            return nexmo_send(receiver, sender, get_contact_string(contacts[0].object))
        response_string = get_string_from_search_contacts(contacts)
        if len(contacts) > 3:
            response_string += "More: https://{}/search/?q={}".format(
                Site.objects.get_current().domain,
                name,
            )
        cache.set(sender, "find:{}".format(name), CACHE_TIMEOUT)
        return nexmo_send(receiver, sender, "Here's what I found for {}:\n{}".format(name, response_string))
    return nexmo_send(receiver, sender, help_message())

@csrf_exempt
def sms(request):
    if request.method == 'GET':
        return handle(
            request.GET.get('msisdn').strip('+'),
            request.GET.get('to').strip('+'),
            request.GET.get('text').strip().lower(),
        )


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


def get_user_objects_from_message(sender):
    sender = '+' + sender
    try:
        profile = Profile.objects.get(phone_number=sender)
        user = profile.user
    except Profile.DoesNotExist:
        return None, None
    try:
        book = Book.objects.filter_for_user(user)[0]
    except IndexError:
        return None, None
    return user, book


def help_message():
    return (
        "Hello! I understand:\n"
        "'Add Jane Doe' to add Jane Doe as a contact\n"
        "'Met Jane Doe' to log that you met Jane Doe\n"
        "'Find Jane Doe' to search for Jane in your contacts"
    )
