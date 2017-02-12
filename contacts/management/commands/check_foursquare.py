import datetime
import foursquare
import logging
import pytz
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialToken, SocialApp

import contacts as contact_settings
from contacts.models import Contact, ContactField, LogEntry, BookOwner

logger = logging.getLogger('scripts')
sentry = logging.getLogger('sentry')


class Command(BaseCommand):

    def handle_checkin(self, checkin):
        created = pytz.utc.localize(
            datetime.datetime.fromtimestamp(checkin['createdAt'])
        )
        for friend_dict in checkin.get('with', []):
            friend = self.get_foursquare_user_details(friend_dict['id'])
            email = friend.get('contact', {}).get('email')
            if email:
                fields = ContactField.objects.for_user(self.user).filter(
                    kind=contact_settings.FIELD_TYPE_EMAIL,
                    value=email,
                    check_for_logs=True,
                    contact__book=self.book,
                )
                if fields:
                    for field in fields:
                        log, was_created = LogEntry.objects.get_or_create(
                            contact=field.contact,
                            logged_by=self.user,
                            time=created,
                            kind='foursquare',
                            external_id=checkin.get('id'),
                            location=checkin.get('venue', {}).get('name'),
                            latitude=checkin.get('venue', {}).get(
                                'location', {}
                            ).get('lat'),
                            longitude=checkin.get('venue', {}).get(
                                'location', {}
                            ).get('lng'),
                            external_location_id=checkin.get('venue', {}).get('id'),
                            link='https://foursquare.com/{}/checkin/{}'.format(
                                self.foursquare_user_id, checkin['id'],
                            )
                        )
                        field.contact.update_last_contact_from_log(log)
                else:
                    name = friend.get('firstName', email)
                    contact = Contact.objects.create(
                        book=self.book,
                        name=name,
                    )
                    email_field = ContactField.objects.create(
                        contact=contact,
                        value=email,
                        label='Email',
                        preferred=True,
                        kind=contact_settings.FIELD_TYPE_EMAIL,
                    )
                    log = LogEntry.objects.create(
                        contact=contact,
                        logged_by=self.user,
                        time=created,
                        kind='foursquare',
                        external_id=checkin.get('id'),
                        location=checkin.get('venue', {}).get('name'),
                        latitude=checkin.get('venue', {}).get(
                            'location', {}
                        ).get('lat'),
                        longitude=checkin.get('venue', {}).get(
                            'location', {}
                        ).get('lng'),
                        external_location_id=checkin.get('venue', {}).get('id'),
                        link='https://foursquare.com/{}/checkin/{}'.format(
                            self.foursquare_user_id, checkin['id'],
                        )
                    )
                    contact.update_last_contact_from_log(log)

    def get_checkins(self):
        checkins = []
        try:
            checkins = self.client.users.checkins().get(
                'checkins', {}
            ).get('items', [])
        except:
            sentry.error(
                'Error getting foursquare checkins', exc_info=True, extra={'user':self.user, 'book': self.book})
        return checkins

    def get_foursquare_user_details(self, id=None):
        user_dict = None
        if id:
            try:
                user_dict = self.client.users(id).get('user', {})
            except:
                sentry.error('Unable to get 4SQ user from ID', exc_info=True, extra={'user': self.user, 'id': id})
        else:
            try:
                user_dict = self.client.users().get('user', {})
            except:
                sentry.error('Unable to get 4SQ user for user', exc_info=True, extra={'user': self.user})
        return user_dict

    def handle(self, *args, **options):
        logger.info("Starting foursquare job")
        app = SocialApp.objects.filter(provider='foursquare')[0]

        for bookowner in BookOwner.objects.filter(check_foursquare=True):
            self.user = bookowner.user
            self.book = bookowner.book
            try:
                token = SocialToken.objects.get(account__user=self.user, app=app)
            except SocialToken.DoesNotExist:
                token = None
                sentry.error("No foursquare token found", exc_info=True, extra={'user':self.user})

            if token:
                self.client = foursquare.Foursquare(access_token=token.token)

            if self.user and self.book and self.client:
                checkins = self.get_checkins()
                self.foursquare_user_id = self.get_foursquare_user_details().get('id')
                for checkin in checkins:
                    self.handle_checkin(checkin)
