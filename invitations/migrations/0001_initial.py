# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contacts', '0003_auto_20150904_2018'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('changed', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('processing', 'processing'), ('error', 'error')], max_length=100, default='pending')),
                ('email', models.EmailField(max_length=254)),
                ('sent', models.DateTimeField(null=True)),
                ('key', models.CharField(unique=True, max_length=32)),
                ('book', models.ForeignKey(to='contacts.Book', null=True, blank=True)),
                ('sender', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
            ],
        ),
    ]
