# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contacts', '0004_auto_20140907_1944'),
    ]

    operations = [
        migrations.AddField(
            model_name='logentry',
            name='logged_by',
            field=models.ForeignKey(related_name=b'logged_by', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
