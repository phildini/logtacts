# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0006_auto_20140908_0346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logentry',
            name='kind',
            field=models.CharField(blank=True, max_length=100, null=True, choices=[(b'twitter', b'Twitter'), (b'tumblr', b'Tumblr'), (b'facebook', b'Facebook'), (b'email', b'Email'), (b'in person', b'In Person'), (b'other', b'Other')]),
        ),
    ]
