from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models


class Tag(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    tag = models.CharField(max_length=100)
    color = models.CharField(max_length=20, blank=True, null=True)
    book = models.ForeignKey('Book', blank=True, null=True)

    def __str__(self):
        return self.tag


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

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('contacts-view', kwargs={'pk': self.id})

    def last_contacted(self):
        last_log = LogEntry.objects.filter(contact=self).latest('created')
        return last_log.created


class Book(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

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
