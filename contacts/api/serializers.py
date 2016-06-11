from rest_framework import serializers
from contacts import models


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LogEntry
        fields = ('id', 'contact', 'kind', 'link', 'time', 'location', 'notes',
            'logged_by', 'created', 'changed')


class ContactFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ContactField
        fields = ('id', 'contact', 'kind', 'label', 'value', 'preferred',
            'created', 'changed')


class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Contact
        fields = ('id', 'book', 'name', 'notes', 'tags', 'created', 'changed')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ('id', 'book', 'tag', 'color', 'created', 'changed')
