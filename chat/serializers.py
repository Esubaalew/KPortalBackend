from rest_framework import serializers
from .models import ChatRoom, Message
from portal.serializers import CustomUserSerializer


class ChatRoomSerializer(serializers.ModelSerializer):
    participants = CustomUserSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'description', 'room_type', 'participants']


class MessageSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'user', 'chat_room', 'content', 'timestamp']
