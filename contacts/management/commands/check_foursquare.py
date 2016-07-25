import datetime
import foursquare
import logging
import pytz
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialToken, SocialApp

import contacts as contact_settings
from contacts.models import Contact, ContactField, LogEntry, BookOwner
from profiles.models import Profile


logger = logging.getLogger('scripts')


class Command(BaseCommand):

    def get_user_book_client(self, app, profile):
        user = profile.user
        book = None
        token = None
        client = None

        try:
            book = BookOwner.objects.get(user=user).book
        except BookOwner.DoesNotExist:
            book = None
            logger.error(
                "No BookOwner found for: {} ({})".format(user, user.id)
            )

        try:
            token = SocialToken.objects.get(account__user=user, app=app)
        except SocialToken.DoesNotExist:
            token = None
            logger.error(
                "No foursquare token found for: {} ({})".format(user, user.id),
            )

        if token:
            client = foursquare.Foursquare(access_token=token.token)

        return user, book, client

    def handle_checkin(self, checkin):
        created = pytz.utc.localize(
            datetime.datetime.fromtimestamp(checkin['createdAt'])
        )
        for friend_dict in checkin.get('with', []):
            friend = self.get_foursquare_user_details(friend_dict['id'])
            email = friend.get('contact', {}).get('email')
            if email:
                fields = ContactField.objects.filter(
                    kind=contact_settings.FIELD_TYPE_EMAIL,
                    value=email,
                    check_for_logs=True,
                    contact__book__bookowner__user=self.user,
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
            logger.error(
                'Error getting foursquare checkins for {} ({})'.format(
                    self.user, self.user.id,
                )
            )
        return checkins

    def get_foursquare_user_details(self, id=None):
        user_dict = None
        if id:
            try:
                user_dict = self.client.users(id).get('user', {})
            except:
                logger.error(
                    'Error getting foursquare user details for 4SQ id: {}'.format(
                        id
                    ),
                )
        else:
            try:
                user_dict = self.client.users().get('user', {})
            except:
                logger.error(
                    'Error getting foursquare user details for {} ({})'.format(
                        self.user, self.user.id,
                    ),
                )
        return user_dict

    def handle(self, *args, **options):
        logger.info("Starting foursquare job")
        app = SocialApp.objects.filter(provider='foursquare')[0]

        for profile in Profile.objects.filter(check_foursquare=True):
            self.user, self.book, self.client = self.get_user_book_client(
                app=app, profile=profile,
            )

            if self.user and self.book and self.client:
                checkins = self.get_checkins()
                self.foursquare_user_id = self.get_foursquare_user_details().get('id')
                for checkin in checkins:
                    self.handle_checkin(checkin)
