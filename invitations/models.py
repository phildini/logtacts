from django.contrib.auth.models import User
from django.db import models
from django.utils.crypto import get_random_string
from simple_history.models import HistoricalRecords
from contacts.models import Book


class InvitationManager(models.Manager):

    def create(self, *args, **kwargs):
        print("create called")
        kwargs['key'] = get_random_string(32).lower()
        return super(InvitationManager, self).create(*args, **kwargs)


class Invitation(models.Model):
    PENDING = 'pending'
    PROCESSING = 'processing'
    ERROR = 'error'
    SENT = 'sent'
    ACCEPTED = 'accepted'

    STATUSES = (
        (PENDING, PENDING),
        (PROCESSING, PROCESSING),
        (ERROR, ERROR),
        (SENT, SENT),
        (ACCEPTED, ACCEPTED),
    )

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=100,
        choices=STATUSES,
        default=PENDING,
    )
    email = models.EmailField()
    sent = models.DateTimeField(null=True)
    sender = models.ForeignKey(User)
    book = models.ForeignKey(Book, blank=True, null=True)
    key = models.CharField(max_length=32, unique=True)
    history = HistoricalRecords()

    objects = InvitationManager()

    def __str__(self):
        return "{} invited {} to {}".format(
            self.sender, self.email, self.book,
        )
    
