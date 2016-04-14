import collections
from six.moves.urllib.parse import quote_plus
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
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

    @property
    def preferred_email(self):
        if not (hasattr(self, '_preferred_email') and self._preferred_email):
            self._preferred_email = ''
            emails = self.emails().values_list('preferred', 'value')
            if emails:
                preferred_emails = [
                    email for email in emails if email[0] == True
                ]
                if len(preferred_emails) > 0:
                    self._preferred_email = preferred_emails[0][1]
                else:
                    self._preferred_email = emails[0][1]
        return self._preferred_email

    @property
    def preferred_address(self):
        if not (hasattr(self, '_preferred_address') and self._preferred_address):
            self._preferred_address = ''
            addresses = self.addresses().values_list('preferred', 'value')
            if addresses:
                preferred_addresses = [
                    address for address in addresses if address[0] == True
                ]
                if len(preferred_addresses) > 0:
                    self._preferred_address = preferred_addresses[0][1]
                else:
                    self._preferred_address = addresses[0][1]
        return self._preferred_address

    @property
    def contactfields(self):
        if not (hasattr(self, '_contactfields') and self._contactfields):
            self._contactfields = ContactField.objects.filter(contact=self)
        return self._contactfields

    def emails(self):
        if not (hasattr(self, '_emails') and self._emails):
            self._emails = self.contactfields.filter(
                kind=contact_settings.FIELD_TYPE_EMAIL,
            )
        return self._emails

    def twitters(self):
        if not (hasattr(self, '_twitters') and self._twitters):
            self._twitters = self.contactfields.filter(
                kind=contact_settings.FIELD_TYPE_TWITTER,
            )
        return self._twitters

    def phones(self):
        if not (hasattr(self, '_phones') and self._phones):
            self._phones = self.contactfields.filter(
                kind=contact_settings.FIELD_TYPE_PHONE,
            )
        return self._phones

    def urls(self):
        if not (hasattr(self, '_urls') and self._urls):
            self._urls = self.contactfields.filter(
                kind=contact_settings.FIELD_TYPE_URL,
            )
        return self._urls

    def dates(self):
        if not (hasattr(self, '_dates') and self._dates):
            self._dates = self.contactfields.filter(
                kind=contact_settings.FIELD_TYPE_DATE,
            )
        return self._dates

    def addresses(self):
        if not (hasattr(self, '_addresses') and self._addresses):
            self._addresses = self.contactfields.filter(
                kind=contact_settings.FIELD_TYPE_ADDRESS,
            )
        return self._addresses

    def generics(self):
        if not (hasattr(self, '_generics') and self._generics):
            self._generics = self.contactfields.filter(
                kind=contact_settings.FIELD_TYPE_TEXT,
            )
        return self._generics


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
    preferred = models.BooleanField(default=False)
    value = models.TextField()
    history = HistoricalRecords()

    def url_quoted(self):
        return quote_plus(
            self.value.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
        )


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


class LogEntryManager(models.Manager):

    def logs_for_user_book(self, user):
        return self.filter(contact__book__bookowner__user=user)

    def logs_for_user_and_tag(self, user, tag):
        return self.filter(
            contact__tags__id=tag.pk,contact__book__bookowner__user=user,
        )


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

    objects = LogEntryManager()

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
