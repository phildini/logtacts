from datetime import timedelta
from django.contrib import admin
from django.utils import timezone
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Contact,
    ContactField,
    RemoteContact,
    Tag,
    Book,
    BookOwner,
    LogEntry,
)

import payments as payments_constants


class BookAdmin(SimpleHistoryAdmin):
    actions = ['gift_one_month', 'gift_one_year']

    def gift_time(self, request, queryset, num_weeks):
        num_books = queryset.count()
        for book in queryset:
            num_owners = BookOwner.objects.filter(book=book).count()
            if num_owners > payments_constants.PLANS[payments_constants.FAMILY_MONTHLY]['collaborators']:
                book.plan = payments_constants.TEAM_MONTHLY
            elif num_owners > payments_constants.PLANS[payments_constants.BASIC_MONTHLY]['collaborators']:
                book.plan = payments_constants.FAMILY_MONTHLY
            if book.paid_until:
                book.paid_until = book.paid_until + timedelta(weeks=num_weeks)
            else:
                book.paid_until = timezone.now() + timedelta(weeks=num_weeks)
            book.save()
        self.message_user(request, "{} books extended for {} weeks".format(num_books, num_weeks))

    def gift_one_month(self, request, queryset):
        self.gift_time(request, queryset, num_weeks=4)
    gift_one_month.short_description = "Gift one month at current plan"

    def gift_one_year(self, request, queryset):
        self.gift_time(request, queryset, num_weeks=52)
    gift_one_year.short_description = "Gift one year at current plan"


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
admin.site.register(Book, BookAdmin)
admin.site.register(BookOwner, SimpleHistoryAdmin)
admin.site.register(LogEntry, LogAdmin)
admin.site.register(ContactField, ContactFieldAdmin)
admin.site.register(RemoteContact)
