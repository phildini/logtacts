from rest_framework import serializers
from contacts import models


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contact
        fields = ('id', 'book', 'name', 'email', 'twitter', 'tumblr', 'website',
            'cell_phone', 'home_phone', 'company', 'address', 'notes', 'tags')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ('id', 'book', 'tag', 'color')


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LogEntry
        fields = ('id', 'contact', 'kind', 'link', 'time', 'location', 'notes')