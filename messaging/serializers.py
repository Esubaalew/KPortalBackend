from django.db.models import Q
from rest_framework import serializers
from portal.serializers import CustomUserSerializer
from .models import Group, Message


class GroupSerializer(serializers.ModelSerializer):
    members = CustomUserSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'members']


class MessageSerializer(serializers.ModelSerializer):
    sender = CustomUserSerializer(read_only=True)
    recipient = CustomUserSerializer(read_only=True)
    group = GroupSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'group', 'content', 'timestamp']


class LatestMessageSerializer(serializers.ModelSerializer):
    sender = CustomUserSerializer(read_only=True)
    recipient = CustomUserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'content', 'timestamp']


class PrivateChatSerializer(serializers.Serializer):
    user = CustomUserSerializer()
    latest_message = LatestMessageSerializer()
