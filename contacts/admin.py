from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Contact,
    ContactField,
    Tag,
    Book,
    BookOwner,
    LogEntry,
)

class ContactAdmin(SimpleHistoryAdmin):
    list_display = (
        'name',
        'book',
        'last_contact',
        'created',
        'changed'
    )

class TagAdmin(SimpleHistoryAdmin):
    list_display = (
        'tag',
        'book',
        'created',
        'changed',
    )


class ContactFieldAdmin(SimpleHistoryAdmin):
    list_display = (
        'value',
        'kind',
        'contact',
        'created',
        'changed',
        'preferred',
    )


class LogAdmin(SimpleHistoryAdmin):
    list_display = (
        'contact',
        'kind',
        'created',
        'time',
    )

admin.site.register(Contact, ContactAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Book, SimpleHistoryAdmin)
admin.site.register(BookOwner, SimpleHistoryAdmin)
admin.site.register(LogEntry, LogAdmin)
admin.site.register(ContactField, ContactFieldAdmin)
