# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0008_contact_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logentry',
            name='kind',
            field=models.CharField(blank=True, max_length=100, null=True, choices=[(b'twitter', b'Twitter'), (b'tumblr', b'Tumblr'), (b'facebook', b'Facebook'), (b'email', b'Email'), (b'in person', b'In Person'), (b'website', b'Website'), (b'other', b'Other')]),
        ),
    ]
