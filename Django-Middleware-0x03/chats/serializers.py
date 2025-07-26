# chats/serializers.py

from rest_framework import serializers
from .models import Conversation, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ConversationSerializer(serializers.ModelSerializer):
    # This is likely the problematic part:
    # If you have 'conversation_id' listed here, remove it.
    # It should NOT be a field that you explicitly provide when creating a Conversation.
    # The 'id' of the conversation is auto-generated.

    participants = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True
    )

    class Meta:
        model = Conversation
        # Ensure 'id' is listed if you want it to be included in the response (read-only)
        # And make sure 'conversation_id' is NOT in this list, unless your Conversation model
        # explicitly has a field named 'conversation_id' (which is highly unlikely and redundant).
        fields = ['id', 'participants', 'created_at', 'updated_at'] # OR whatever fields you have
        read_only_fields = ['id', 'created_at', 'updated_at'] # 'id' should usually be read-only