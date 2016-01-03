from rest_framework import serializers
from contacts import models


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contact
        fields = ('id', 'name', 'email', 'twitter', 'tumblr', 'website',
            'cell_phone', 'home_phone', 'company', 'address', 'notes')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ('id', 'tag', 'color', 'book')