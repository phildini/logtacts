# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('changed', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('changed', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=100, null=True, blank=True)),
                ('twitter', models.CharField(max_length=140, null=True, blank=True)),
                ('tumblr', models.CharField(max_length=255, null=True, blank=True)),
                ('website', models.URLField(max_length=255, null=True, blank=True)),
                ('portfolio', models.URLField(max_length=255, null=True, blank=True)),
                ('cell_phone', models.CharField(max_length=20, null=True, blank=True)),
                ('home_phone', models.CharField(max_length=20, null=True, blank=True)),
                ('notes', models.TextField()),
                ('book', models.ForeignKey(to='contacts.Book')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('changed', models.DateTimeField(auto_now=True)),
                ('kind', models.CharField(max_length=100, null=True, blank=True)),
                ('time', models.DateTimeField(null=True, blank=True)),
                ('location', models.CharField(max_length=255, null=True, blank=True)),
                ('notes', models.TextField()),
                ('contact', models.ForeignKey(to='contacts.Contact')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('changed', models.DateTimeField(auto_now=True)),
                ('tag', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=20, null=True, blank=True)),
                ('book', models.ForeignKey(to='contacts.Book')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
