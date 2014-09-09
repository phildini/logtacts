# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0005_logentry_logged_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='book',
            field=models.ForeignKey(blank=True, to='contacts.Book', null=True),
        ),
    ]
