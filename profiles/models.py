from django.contrib.auth.models import User
from django.db import models
from simple_history.models import HistoricalRecords


class Profile(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User)
    send_contact_reminders = models.BooleanField(default=False)
    send_birthday_reminders = models.BooleanField(default=False)
    check_twitter_dms = models.BooleanField(default=True)
    check_twitter_mentions = models.BooleanField(default=True)
    check_foursquare = models.BooleanField(default=True)
    history = HistoricalRecords()

    def __str__(self):
        return "{}'s profile".format(self.user)
