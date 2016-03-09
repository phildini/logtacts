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
    logentry_set = LogSerializer(many=True, read_only=True)
    contactfield_set = ContactFieldSerializer(many=True)

    class Meta:
        model = models.Contact
        fields = ('id', 'book', 'name', 'notes', 'tags', 'created', 'changed',
            'logentry_set', 'contactfield_set')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ('id', 'book', 'tag', 'color', 'created', 'changed')
