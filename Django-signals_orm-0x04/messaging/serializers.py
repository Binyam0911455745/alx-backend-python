# Django-signals_orm-0x04/messaging/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

User = get_user_model()

# Assuming you have a UserSerializer defined somewhere, e.g.:
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class MessageHistorySerializer(serializers.ModelSerializer):
    # If you added edited_by, include it here
    edited_by = UserSerializer(read_only=True) # Or StringRelatedField()

    class Meta:
        model = MessageHistory
        fields = ['id', 'old_content', 'edited_at', 'edited_by'] # Include edited_by
        read_only_fields = ['edited_at']


# THIS IS THE CRUCIAL PART: Ensure this class is present and correct
class RecursiveReplySerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField() # This makes it recursive

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'is_read', 'edited', 'parent_message', 'replies']
        read_only_fields = ['timestamp', 'is_read', 'edited']

    def get_replies(self, obj):
        # Ensure prefetch_related is used in the view for efficiency
        # The 'replies' field should already be prefetched by the view's get_queryset.
        # This will call the RecursiveReplySerializer for each reply, creating the tree structure.
        return RecursiveReplySerializer(obj.replies.all().order_by('timestamp'), many=True, context=self.context).data


class MessageDetailSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    history = MessageHistorySerializer(many=True, read_only=True)
    replies = RecursiveReplySerializer(many=True, read_only=True) # Use the recursive serializer here

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'is_read', 'edited', 'history', 'parent_message', 'replies']
        read_only_fields = ['timestamp', 'is_read', 'edited', 'history', 'replies']


# And if you chose Option 1 for NotificationSerializer in the previous step:
class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # Or serializers.StringRelatedField()
    message = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'content', 'timestamp', 'is_read']