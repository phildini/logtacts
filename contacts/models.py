from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models


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

    objects = TagManager()

    def __str__(self):
        return self.tag

    def can_be_viewed_by(self, user):
        return bool(self.book.bookowner_set.filter(user=user))

    def can_be_edited_by(self, user):
        return bool(self.book.bookowner_set.filter(user=user))


class ContactManager(models.Manager):

    def get_contacts_for_user(self, user):
        return self.filter(
            book__bookowner__user=user,
        )


class Contact(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
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
    tags = models.ManyToManyField(Tag, blank=True)

    objects = ContactManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('contacts-view', kwargs={'pk': self.id})

    def last_contacted(self):
        last_log = LogEntry.objects.filter(contact=self).latest('created')
        return last_log.created

    def can_be_viewed_by(self, user):
        return bool(self.book.bookowner_set.filter(user=user))

    def can_be_edited_by(self, user):
        return bool(self.book.bookowner_set.filter(user=user))


class Book(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)

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
