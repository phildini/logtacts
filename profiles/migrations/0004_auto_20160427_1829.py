# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-27 18:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_historicalprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalprofile',
            name='send_birthday_reminders',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='send_birthday_reminders',
            field=models.BooleanField(default=False),
        ),
    ]
