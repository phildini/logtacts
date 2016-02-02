from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from simple_history.admin import SimpleHistoryAdmin
from . import models

class ActiveUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'last_login',
        'is_active',
        'is_staff',
    )

admin.site.unregister(User)
admin.site.register(User, ActiveUserAdmin)

admin.site.register(models.Profile, SimpleHistoryAdmin)