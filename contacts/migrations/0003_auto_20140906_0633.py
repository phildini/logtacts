# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0002_auto_20140906_0626'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contact',
            name='book',
        ),
        migrations.AddField(
            model_name='contact',
            name='tags',
            field=models.ManyToManyField(to='contacts.Tag'),
            preserve_default=True,
        ),
    ]
