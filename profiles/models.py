from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User)
    send_contact_reminders = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return "{}'s profile".format(self.user)
