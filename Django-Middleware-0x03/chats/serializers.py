# Django-Middleware-0x03/chats/serializers.py

from rest_framework import serializers
from .models import Message, Conversation, User # Assuming these models exist in chats/models.py

# Serializer for the custom User model (if you have one and want to expose it)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name'] # Or other relevant fields

# Serializer for a Message
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True) # Display sender details, but don't allow setting on create
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='sender', write_only=True
    ) # Allow setting sender by ID for create/update

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_id', 'content', 'timestamp']
        read_only_fields = ['timestamp']

# Serializer for a Conversation
class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True) # Display participant details
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True, source='participants'
    ) # Allow setting participants by IDs

    messages = MessageSerializer(many=True, read_only=True) # Nested messages

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'participant_ids', 'topic', 'messages', 'created_at']
        read_only_fields = ['created_at']