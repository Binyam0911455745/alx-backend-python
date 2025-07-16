# C:\Users\user\alx-backend-python\messaging_app\chats\serializers.py

from rest_framework import serializers
from .models import User, Conversation, Message
from django.contrib.auth import get_user_model
from . import models # Assuming you use 'from . import models'

User = get_user_model()

# We'll need a simple User serializer for nested representation
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email'] # Only expose necessary user info

class MessageSerializer(serializers.ModelSerializer):
    # We want to display the sender's username, not just their ID
    sender = UserSerializer(read_only=True) # Use our custom UserSerializer

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'content', 'timestamp']
        read_only_fields = ['sender', 'timestamp'] # These fields are set by the server

class ConversationSerializer(serializers.ModelSerializer):
    # This field is for receiving a list of participant IDs when creating/updating
    # It is write_only because we want to output the full participant objects on GET
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    # To represent participants on GET, you might use StringRelatedField or nested serializer
    participants = serializers.StringRelatedField(many=True, read_only=True) # Good for display

    class Meta:
        model = models.Conversation
        # IMPORTANT: Include 'participant_ids' in the fields here!
        fields = ['id', 'name', 'participants', 'participant_ids']
        read_only_fields = ['id'] # IDs are usually read-only

    def create(self, validated_data):
        participants_data = validated_data.pop('participant_ids', [])
        chat = Chat.objects.create(**validated_data)
        chat.participants.set(participants_data) # Add participants after chat creation
        return chat

    def update(self, instance, validated_data):
        participants_data = validated_data.pop('participant_ids', None)
        if participants_data is not None:
            instance.participants.set(participants_data) # Update participants
        return super().update(instance, validated_data)
class MessageSerializer(serializers.ModelSerializer):
    # Display sender's username, but allow sender to be set automatically by view
    sender = serializers.ReadOnlyField(source='sender.username')
    # If you want to show the conversation ID:
    conversation = serializers.PrimaryKeyRelatedField(queryset=Conversation.objects.all())


    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'content', 'timestamp', 'is_read']
        read_only_fields = ['sender', 'timestamp'] # Sender and timestamp are set by the server