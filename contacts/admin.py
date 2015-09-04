from django.contrib import admin
from .models import (
    Contact,
    Tag,
    Book,
    BookOwner,
    LogEntry,
)

admin.site.register(Contact)
admin.site.register(Tag)
admin.site.register(Book)
admin.site.register(BookOwner)
admin.site.register(LogEntry)
