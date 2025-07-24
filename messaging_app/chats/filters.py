# alx-backend-python/messaging_app/chats/filters.py

import django_filters
from django.contrib.auth import get_user_model
from .models import Message, Conversation # Import your models

User = get_user_model()

class MessageFilter(django_filters.FilterSet):
    # Filter messages sent by a specific user (using sender's username)
    # Assumes Message model has a 'sender' ForeignKey to User
    sender_username = django_filters.CharFilter(
        field_name='sender__username', lookup_expr='iexact',
        help_text="Filter messages by the exact username of the sender (case-insensitive)."
    )

    # Filter messages within a time range (e.g., messages created after a certain date)
    # Assumes Message model has a 'timestamp' DateTimeField
    min_timestamp = django_filters.DateTimeFilter(
        field_name="timestamp", lookup_expr='gte',
        help_text="Filter messages created on or after this timestamp (YYYY-MM-DDTHH:MM:SSZ)."
    )
    max_timestamp = django_filters.DateTimeFilter(
        field_name="timestamp", lookup_expr='lte',
        help_text="Filter messages created on or before this timestamp (YYYY-MM-DDTHH:MM:SSZ)."
    )

    # Optional: Filter messages within a specific conversation
    conversation_id = django_filters.NumberFilter(
        field_name="conversation__id", lookup_expr='exact',
        help_text="Filter messages by conversation ID."
    )


    class Meta:
        model = Message
        fields = ['sender_username', 'min_timestamp', 'max_timestamp', 'conversation_id']

# You might also want a ConversationFilter if needed for conversations
class ConversationFilter(django_filters.FilterSet):
    # Filter conversations by a participant's username
    participant_username = django_filters.CharFilter(
        field_name='participants__username', lookup_expr='iexact',
        help_text="Filter conversations by a participant's exact username (case-insensitive)."
    )

    class Meta:
        model = Conversation
        fields = ['participant_username']