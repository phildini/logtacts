# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitations', '0002_auto_20150905_1747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitation',
            name='status',
            field=models.CharField(default='pending', max_length=100, choices=[('pending', 'pending'), ('processing', 'processing'), ('error', 'error'), ('sent', 'sent'), ('accepted', 'accepted')]),
        ),
    ]
