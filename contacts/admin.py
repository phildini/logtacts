from django.contrib import admin
from .models import (
    Contact,
    Tag,
    Book,
    LogEntry,
)

admin.site.register(Contact)
admin.site.register(Tag)
admin.site.register(Book)
admin.site.register(LogEntry)
