# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0003_auto_20140906_0633'),
    ]

    operations = [
        migrations.AddField(
            model_name='logentry',
            name='link',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contact',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='tags',
            field=models.ManyToManyField(to=b'contacts.Tag', blank=True),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='notes',
            field=models.TextField(blank=True),
        ),
    ]
