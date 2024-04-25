from rest_framework import serializers
from .models import CustomUser, Resource


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'bio']


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'language', 'caption', 'topic', 'owner', 'url', 'file', 'photo', 'date_shared', 'date_modified']
