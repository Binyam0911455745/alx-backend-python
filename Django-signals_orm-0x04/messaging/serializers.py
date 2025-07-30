# Django-signals_orm-0x04/messaging/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class MessageHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageHistory
        fields = ['old_content', 'edited_at']
        read_only_fields = ['edited_at']

# Make sure this entire class is present and correctly indented
class MessageDetailSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    history = MessageHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'is_read', 'edited', 'history']
        read_only_fields = ['timestamp', 'is_read', 'edited', 'history']