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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('changed', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('changed', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, blank=True, null=True)),
                ('twitter', models.CharField(max_length=140, blank=True, null=True)),
                ('tumblr', models.CharField(max_length=255, blank=True, null=True)),
                ('website', models.URLField(max_length=255, blank=True, null=True)),
                ('portfolio', models.URLField(max_length=255, blank=True, null=True)),
                ('cell_phone', models.CharField(max_length=20, blank=True, null=True)),
                ('home_phone', models.CharField(max_length=20, blank=True, null=True)),
                ('company', models.CharField(max_length=100, blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('changed', models.DateTimeField(auto_now=True)),
                ('kind', models.CharField(max_length=100, choices=[('twitter', 'Twitter'), ('tumblr', 'Tumblr'), ('facebook', 'Facebook'), ('email', 'Email'), ('in person', 'In Person'), ('website', 'Website'), ('other', 'Other')], blank=True, null=True)),
                ('link', models.URLField(blank=True, null=True)),
                ('time', models.DateTimeField(blank=True, null=True)),
                ('location', models.CharField(max_length=255, blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('contact', models.ForeignKey(to='contacts.Contact')),
                ('logged_by', models.ForeignKey(related_name='logged_by', blank=True, null=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('changed', models.DateTimeField(auto_now=True)),
                ('tag', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=20, blank=True, null=True)),
                ('book', models.ForeignKey(blank=True, null=True, to='contacts.Book')),
            ],
        ),
        migrations.AddField(
            model_name='contact',
            name='tags',
            field=models.ManyToManyField(to='contacts.Tag', blank=True),
        ),
    ]
