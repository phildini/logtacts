import logging
import pytz
import tweepy
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialToken, SocialApp

import contacts as contact_settings
from contacts.models import Contact, ContactField, LogEntry, BookOwner
from profiles.models import Profile


logger = logging.getLogger('scripts')
sentry = logging.getLogger('sentry')


class Command(BaseCommand):

    help = "Check twitter and update contacts"

    def setup_twitter_app_creds(self):
        try:
            twitter_app_creds = SocialApp.objects.filter(provider='twitter')[0]
            self.twitter_key = twitter_app_creds.client_id
            self.twitter_secret = twitter_app_creds.secret
        except IndexError:
            sentry.error("Couldn't find twitter app creds", exc_info=True)

    def get_messages(self, user, token):
        messages = None
        if token:
            try:
                auth = tweepy.OAuthHandler(self.twitter_key, self.twitter_secret)
                auth.set_access_token(token.token, token.token_secret)
                api = tweepy.API(auth)
                logger.info(
                    "Fetching messages for {} ({})".format(user, user.id),
                    )
                messages = api.direct_messages()
            except:
                sentry.error("Error fetching twitter messages", exc_info=True, extra={'user':user})
        return messages

    def create_log_or_contact_for_message(self, message):
        created = pytz.utc.localize(message.created_at)
        fields = ContactField.objects.for_user(self.user).filter(
            kind=contact_settings.FIELD_TYPE_TWITTER,
            value=message.sender.screen_name,
            check_for_logs=True,
            contact__book=self.book,
        )
        if fields:
            for field in fields:
                days_since_last = None
                try:
                    last_log = LogEntry.objects.filter(
                        contact=field.contact,
                        logged_by=self.user,
                        kind='twitter',
                    ).latest('time')
                except LogEntry.DoesNotExist:
                    last_log = None
                if last_log:
                    if last_log.time:
                        days_since_last = (created - last_log.time).days
                    elif last_log.created:
                        days_since_last = (created - last_log.created).days
                if not days_since_last or days_since_last >= 0:
                    log, created = LogEntry.objects.get_or_create(
                        contact=field.contact,
                        logged_by=self.user,
                        time=created,
                        kind='twitter',
                    )
                    field.contact.update_last_contact_from_log(log)
        else:
            contact = Contact.objects.create(
                book=self.book,
                name=message.sender.name,
            )
            ContactField.objects.create(
                contact=contact,
                kind=contact_settings.FIELD_TYPE_TWITTER,
                value=message.sender.screen_name,
                label="Twitter",
            )
            log = LogEntry.objects.create(
                contact=contact,
                logged_by=self.user,
                time=created,
                kind='twitter',
            )
            contact.update_last_contact_from_log(log)

    def handle(self, *args, **options):
        logger.info("Starting twitter job")

        self.setup_twitter_app_creds()

        opted_into_dms = BookOwner.objects.filter(check_twitter_dms=True)
        for bookowner in opted_into_dms:
            self.user = bookowner.user
            self.book = bookowner.book

            try:
                token = SocialToken.objects.get(
                    account__user=self.user,
                    app__provider='twitter',
                )
            except SocialToken.DoesNotExist:
                sentry.error("No twitter token for user", exc_info=True, extra={'user': self.user, 'book': book})

            messages = self.get_messages(self.user, self.token)

            if messages:
                for message in messages:
                    self.create_log_or_contact_for_message(message)

        logger.info("Finishing twitter job")
