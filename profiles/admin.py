from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from . import models

admin.site.register(models.Profile, SimpleHistoryAdmin)