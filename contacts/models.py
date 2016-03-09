import collections
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from jsonfield import JSONField
from simple_history.models import HistoricalRecords

import contacts as contact_settings

class TagManager(models.Manager):

    def get_tags_for_user(self, user):
        return self.filter(
            book__bookowner__user=user,
        )


class Tag(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    tag = models.CharField(max_length=100)
    color = models.CharField(max_length=20, blank=True, null=True)
    book = models.ForeignKey('Book', blank=True, null=True)
    history = HistoricalRecords()

    objects = TagManager()

    def __str__(self):
        return self.tag

    def can_be_viewed_by(self, user):
        return bool(self.book.bookowner_set.filter(user=user))

    def can_be_edited_by(self, user):
        return bool(self.book.bookowner_set.filter(user=user))

    @property
    def corrected_color(self):
        if self.color:
            if self.color.startswith('#'):
                return self.color
            return '#' + self.color
        return '#123456'


class ContactManager(models.Manager):

    def get_contacts_for_user(self, user):
        return self.filter(
            book__bookowner__user=user,
        )


class Contact(models.Model):
    

    FIELD_TYPES = (
        (contact_settings.FIELD_TYPE_EMAIL, 'Email'),
        (contact_settings.FIELD_TYPE_URL, 'URL'),
        (contact_settings.FIELD_TYPE_DATE,'Date'),
        (contact_settings.FIELD_TYPE_TWITTER, 'Twitter'),
        (contact_settings.FIELD_TYPE_PHONE, 'Phone'),
        (contact_settings.FIELD_TYPE_ADDRESS, 'Address'),
        (contact_settings.FIELD_TYPE_TEXT, 'Short Text'),
        (contact_settings.FIELD_TYPE_BIG_TEXT, 'Big Text'),
    )

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    last_contact = models.DateTimeField(blank=True, null=True)
    book = models.ForeignKey('Book', blank=True, null=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    twitter = models.CharField(max_length=140, blank=True, null=True)
    tumblr = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True)
    portfolio = models.URLField(max_length=255, blank=True, null=True)
    cell_phone = models.CharField(max_length=20, blank=True, null=True)
    home_phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    should_surface = models.BooleanField(blank=True, default=True)
    birthday = models.DateField(blank=True, null=True)
    work_phone = models.CharField(max_length=20, blank=True)
    work_email = models.EmailField(blank=True)
    document = JSONField(
        blank=True,
        load_kwargs={'object_pairs_hook': collections.OrderedDict},
    )
    tags = models.ManyToManyField(Tag, blank=True)
    history = HistoricalRecords()

    objects = ContactManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('contacts-view', kwargs={'pk': self.id})

    def last_contacted(self):
        if self.last_contact:
            return self.last_contact

    def can_be_viewed_by(self, user):
        return bool(self.book.bookowner_set.filter(user=user))

    def can_be_edited_by(self, user):
        return bool(self.book.bookowner_set.filter(user=user))

    def preferred_email(self):
        try:
            return ContactField.objects.get(
                contact=self,
                kind=contact_settings.FIELD_TYPE_EMAIL,
                preferred=True,
            ).value
        except ContactField.DoesNotExist:
            try:
                return ContactField.objects.filter(
                    contact=self,
                    kind=contact_settings.FIELD_TYPE_EMAIL,
                )[0].value
            except IndexError:
                return ''

    def preferred_address(self):
        try:
            return ContactField.objects.get(
                contact=self,
                kind=contact_settings.FIELD_TYPE_ADDRESS,
                preferred=True,
            ).value
        except ContactField.DoesNotExist:
            try:
                return ContactField.objects.filter(
                    contact=self,
                    kind=contact_settings.FIELD_TYPE_ADDRESS,
                )[0].value
            except IndexError:
                return ''

    def fields(self):
        return ContactField.objects.filter(contact=self)

    def emails(self):
        return self.fields().filter(kind=contact_settings.FIELD_TYPE_EMAIL)

    def twitters(self):
        return self.fields().filter(kind=contact_settings.FIELD_TYPE_TWITTER)

    def phones(self):
        return self.fields().filter(kind=contact_settings.FIELD_TYPE_PHONE)

    def urls(self):
        return self.fields().filter(kind=contact_settings.FIELD_TYPE_URL)

    def dates(self):
        return self.fields().filter(kind=contact_settings.FIELD_TYPE_DATE)

    def addresses(self):
        return self.fields().filter(kind=contact_settings.FIELD_TYPE_ADDRESS)

    def generics(self):
        return self.fields().filter(kind=contact_settings.FIELD_TYPE_TEXT)


class ContactField(models.Model):

    FIELD_TYPES = (
        (contact_settings.FIELD_TYPE_EMAIL, 'Email'),
        (contact_settings.FIELD_TYPE_URL, 'URL'),
        (contact_settings.FIELD_TYPE_DATE,'Date'),
        (contact_settings.FIELD_TYPE_TWITTER, 'Twitter'),
        (contact_settings.FIELD_TYPE_PHONE, 'Phone'),
        (contact_settings.FIELD_TYPE_ADDRESS, 'Address'),
        (contact_settings.FIELD_TYPE_TEXT, 'Short Text'),
        (contact_settings.FIELD_TYPE_BIG_TEXT, 'Big Text'),
    )

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    contact = models.ForeignKey(Contact)
    label = models.CharField(max_length=100)
    kind = kind = models.CharField(
        max_length=100,
        choices=FIELD_TYPES,
    )
    preferred = models.BooleanField(default=True)
    value = models.TextField()
    history = HistoricalRecords()


class Book(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    def can_be_viewed_by(self, user):
        return bool(self.bookowner_set.filter(user=user))

    def can_be_edited_by(self, user):
        return bool(self.bookowner_set.filter(user=user))

class BookOwner(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    book = models.ForeignKey('Book')
    user = models.ForeignKey(User)
    history = HistoricalRecords()

    def __str__(self):
        return "{} is an owner of {}".format(self.user, self.book)


class LogEntry(models.Model):
    KIND_CHOICES = (
        ('twitter', 'Twitter'),
        ('tumblr', 'Tumblr'),
        ('facebook', 'Facebook'),
        ('email', 'Email'),
        ('in person', 'In Person'),
        ('website', 'Website'),
        ('other', 'Other'),
        ('edit', 'Edit')
    )

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    contact = models.ForeignKey('Contact')
    kind = models.CharField(
        max_length=100,
        choices=KIND_CHOICES,
        blank=True,
        null=True,
    )
    link = models.URLField(blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    logged_by = models.ForeignKey(User, blank=True, null=True, related_name='logged_by')
    notes = models.TextField(blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return "Log on %s" % (self.contact,)

    @property
    def display_time(self):
        if self.time:
            return self.time
        else:
            return self.created

    @property
    def action_str(self):
        if self.kind in ('twitter', 'tumblr', 'facebook', 'email'):
            return 'chatted with {} via {}'.format(self.contact, self.kind)
        if self.kind == 'in person':
            return 'met with {}'.format(self.contact)
        if self.kind == 'edit':
            return "edited {}'s contact info".format(self.contact)
        return 'contacted {}'.format(self.contact)

    def can_be_viewed_by(self, user):
        return bool(self.contact.book.bookowner_set.filter(user=user))

    def can_be_edited_by(self, user):
        return bool(self.contact.book.bookowner_set.filter(user=user))
