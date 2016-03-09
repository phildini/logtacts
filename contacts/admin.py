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
    )

admin.site.register(Contact, ContactAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Book, SimpleHistoryAdmin)
admin.site.register(BookOwner, SimpleHistoryAdmin)
admin.site.register(LogEntry, SimpleHistoryAdmin)
admin.site.register(ContactField, ContactFieldAdmin)
