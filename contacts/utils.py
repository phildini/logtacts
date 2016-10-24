import httplib2
import logging
import time

from apiclient.discovery import build
from oauth2client.client import (
    HttpAccessTokenRefreshError,
    GoogleCredentials,
)
from oauth2client import GOOGLE_TOKEN_URI
from allauth.socialaccount.models import SocialToken, SocialApp
from googleapiclient.errors import HttpError
from django.contrib.auth.models import User

import contacts as contact_settings

from contacts.models import (
    Book,
    Contact,
    ContactField,
    RemoteContact,
)


logger = logging.getLogger('sentry')


def pull_google_contacts(user, book):
    app = SocialApp.objects.filter(provider='google')[0]
    token = SocialToken.objects.get(account__user=user, app=app)
    creds = GoogleCredentials(
        access_token=token.token,
        token_expiry=None,
        token_uri=GOOGLE_TOKEN_URI,
        client_id=app.client_id,
        client_secret=app.secret,
        refresh_token=None,
        user_agent='Python',
        revoke_uri=None,
    )

    http = httplib2.Http()
    http = creds.authorize(http)
    people_service = build(serviceName='people', version='v1', http=http)

    try:
        connections = people_service.people().connections().list(resourceName='people/me', pageSize=50).execute()
    except HttpError:
        time.sleep(60)
        connections = people_service.people().connections().list(resourceName='people/me', pageSize=50).execute()
    except HttpAccessTokenRefreshError:
        logger.error("Bad google token for: {}".format(user), exc_info=True)
        return

    next_page = connections.get('nextPageToken')
    sync_token = connections.get('nextSyncToken')

    get_expanded_response_and_create_contacts(connections, people_service, sync_token, book)
    try:
        success = True
        while next_page:
            try:
                connections = people_service.people().connections().list(
                    resourceName='people/me', pageSize=50, pageToken=next_page
                ).execute()
            except HttpError:
                time.sleep(60)
                connections = people_service.people().connections().list(
                    resourceName='people/me', pageSize=50, pageToken=next_page
                ).execute()
            get_expanded_response_and_create_contacts(connections, people_service, connections.get('nextSyncToken'), book)
            next_page = connections.get('nextPageToken')
        return success
    except:
        logger.error("Google Import Error", exc_info=True)
        return False

def get_expanded_response_and_create_contacts(connections, people_service, sync_token, book):
    connection_ids = [connection['resourceName'] for connection in connections['connections']]
    try:
        google_response = people_service.people().getBatchGet(resourceNames=connection_ids).execute()
    except HttpError:
        time.sleep(60)
        google_response = people_service.people().getBatchGet(resourceNames=connection_ids).execute()

    for gcontact in google_response['responses']:
        try:
            try:
                rcontact = RemoteContact.objects.get(
                    remote_service='google',
                    remote_id=gcontact['requestedResourceName'],
                    book=book,
                )
                contact = rcontact.contact
            except RemoteContact.DoesNotExist:
                try:
                    contact = Contact.objects.create(
                        book=book,
                        name=gcontact['person']['names'][0]['displayName'],
                    )
                    rcontact = RemoteContact.objects.create(
                        contact=contact,
                        book=book,
                        remote_service='google',
                        remote_id=gcontact['requestedResourceName'],
                    )
                except:
                    break
            if rcontact.sync_token != sync_token:
                rcontact.sync_token = sync_token
                rcontact.save()
                try:
                    for email in gcontact['person'].get('emailAddresses', []):
                        label = email.get('formattedType', email.get('type', 'Email'))
                        value = email['value']
                        if value.startswith(('http://','https://')):
                            break
                        ContactField.objects.get_or_create(
                            contact=contact,
                            kind=contact_settings.FIELD_TYPE_EMAIL,
                            value=email['value'],
                            label=label,
                            preferred=email['metadata'].get('primary', False)
                        )
                except:
                    logger.error("Error adding emails for {}".format(contact), exc_info=True, extra={
                        'gcontact': gcontact
                    })
                try:
                    for birthday in gcontact['person'].get('birthdays', []):
                        try:
                            date_str = "{}-{}-{}".format(
                                birthday['date']['year'],
                                birthday['date']['month'],
                                birthday['date']['day'],
                            )
                            ContactField.objects.get_or_create(
                                contact=contact,
                                kind=contact_settings.FIELD_TYPE_DATE,
                                value=date_str,
                                label='Birthday',
                                preferred=birthday['metadata'].get('primary', False)
                            )
                        except KeyError:
                            pass
                except:
                    logger.error("Error adding birthdays for {}".format(contact), exc_info=True, extra={
                        'gcontact': gcontact
                    })
                try:
                    for organization in gcontact['person'].get('organizations', []):
                        if organization.get('title'):
                            ContactField.objects.get_or_create(
                                contact=contact,
                                kind=contact_settings.FIELD_TYPE_TEXT,
                                value=organization['title'],
                                label='Title',
                                preferred=organization['metadata'].get('primary', False)
                            )
                        if organization.get('name'):
                            ContactField.objects.get_or_create(
                                contact=contact,
                                kind=contact_settings.FIELD_TYPE_TEXT,
                                value=organization['name'],
                                label='Company',
                                preferred=organization['metadata'].get('primary', False)
                            )
                except:
                    logger.error("Error adding organization for {}".format(contact), exc_info=True, extra={
                        'gcontact': gcontact
                    })
                # TODO: Photo
                try:
                    for phone in gcontact['person'].get('phoneNumbers', []):
                        value = phone.get('canonicalForm', phone.get('value'))
                        ContactField.objects.get_or_create(
                            contact=contact,
                            kind=contact_settings.FIELD_TYPE_PHONE,
                            value=value,
                            label=phone['formattedType'],
                            preferred=phone['metadata'].get('primary', False)
                        )
                except:
                    logger.error("Error adding phones for {}".format(contact), exc_info=True, extra={
                        'gcontact': gcontact
                    })
                try:
                    for address in gcontact['person'].get('addresses', []):
                        ContactField.objects.get_or_create(
                            contact=contact,
                            kind=contact_settings.FIELD_TYPE_ADDRESS,
                            value=address['formattedValue'],
                            label=address['formattedType'],
                            preferred=address['metadata'].get('primary', False)
                        )
                except:
                    logger.error("Error adding addresses for {}".format(contact), exc_info=True, extra={
                        'gcontact': gcontact
                    })
                try:
                    for photo in gcontact['person'].get('photos', []):
                        if photo['metadata'].get('primary'):
                            contact.photo_url = photo['url']
                            contact.save()
                except:
                    logger.error("Error setting photo for {}".format(contact), exc_info=True, extra={
                        'gcontact': gcontact
                    })
        except:
            logger.error('Error adding contact from google', exc_info=True, extra={'gcontact': gcontact})

