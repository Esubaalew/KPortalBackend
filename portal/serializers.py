from rest_framework import serializers
from .models import CustomUser, LinkResource, FileResource


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'bio']


class LinkResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkResource
        fields = ['id', 'language', 'caption', 'topic', 'resource_type', 'url', 'owner', 'date_shared', 'date_modified']


class FileResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileResource
        fields = ['id', 'language', 'caption', 'topic', 'resource_type', 'file', 'owner', 'date_shared',
                  'date_modified']
