from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Contact,
    Tag,
    Book,
    BookOwner,
    LogEntry,
)

admin.site.register(Contact, SimpleHistoryAdmin)
admin.site.register(Tag, SimpleHistoryAdmin)
admin.site.register(Book, SimpleHistoryAdmin)
admin.site.register(BookOwner, SimpleHistoryAdmin)
admin.site.register(LogEntry, SimpleHistoryAdmin)
