from rest_framework import serializers
from .. import models


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contact
        fields = ('id', 'name', 'twitter', 'tumblr', 'website', 'cell_phone',
            'home_phone', 'company', 'address', 'notes')