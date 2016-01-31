from rest_framework import serializers
from contacts import models


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contact
        fields = ('id', 'book', 'name', 'email', 'twitter', 'tumblr', 'website', 'portfolio',
            'cell_phone', 'home_phone', 'company', 'address', 'notes', 'tags', 'created', 'changed')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ('id', 'book', 'tag', 'color', 'created', 'changed')


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LogEntry
        fields = ('id', 'contact', 'kind', 'link', 'time', 'location', 'notes', 'logged_by', 'created', 'changed')