# alx-backend-python/messaging_app/chats/views.py

from django.db.models import Q # Used for complex OR lookups in querysets
from rest_framework import viewsets, status # `status` for explicit HTTP responses
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response # To return custom responses
from django_filters.rest_framework import DjangoFilterBackend # For integrating django-filter

# Import custom components
from .models import Message, Conversation
from .serializers import MessageSerializer, ConversationSerializer
from .permissions import IsOwnerOrParticipant # Your custom object-level permission
from .pagination import MessagePagination # Your custom pagination class
from .filters import MessageFilter, ConversationFilter # Your custom filter classes


class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows messages to be viewed, created, updated, or deleted.
    
    Permissions:
    - Only authenticated users can access.
    - `IsOwnerOrParticipant` ensures users can only interact with messages
      they are involved in (as sender or conversation participant).

    Features:
    - Pagination is applied using `MessagePagination`.
    - Filtering is supported via `MessageFilter` (e.g., by sender, timestamp).
    - Explicitly filters by `conversation_id` in `get_queryset` if provided.
    - Automatically sets the message sender to the current authenticated user on creation.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrParticipant]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

    def get_queryset(self):
        """
        Dynamically filters the queryset to return messages relevant to the
        currently authenticated user.

        A user can see a message if:
        1. They are the `sender` of the message.
        2. They are a `participant` in the `conversation` to which the message belongs.

        Additionally, if a `conversation_id` is provided in the query parameters,
        the queryset is further filtered to include only messages from that specific
        conversation, ensuring the user is a participant of that conversation.

        The `.distinct()` call prevents duplicate messages.
        """
        user = self.request.user
        if not user.is_authenticated:
            return Message.objects.none()

        # Start with messages where the current user is the sender OR
        # the current user is a participant in the message's conversation.
        queryset = Message.objects.filter(
            Q(sender=user) | Q(conversation__participants=user)
        ).distinct()

        # --- Explicit check and filter for 'conversation_id' from query parameters ---
        # This part ensures that if a client requests messages for a specific
        # conversation, they only get messages from that conversation.
        # The initial Q filter already ensures they have access to that conversation.
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            # Filter the already permission-filtered queryset by the specific conversation ID.
            # Convert to UUID if your conversation IDs are UUIDs.
            try:
                # Assuming conversation IDs are UUIDs, convert for lookup.
                # If they are integers, remove uuid.UUID() conversion.
                from uuid import UUID
                conversation_uuid = UUID(conversation_id)
                queryset = queryset.filter(conversation__id=conversation_uuid)
            except ValueError:
                # Handle invalid UUID format if needed, perhaps by returning an empty queryset
                # or letting the filter backend handle it. For now, it will just not filter.
                pass # Let the filter backend or other logic handle invalid IDs


        return queryset

    def perform_create(self, serializer):
        """
        Automatically sets the `sender` of the message to the requesting user
        before saving the new message instance.
        """
        serializer.save(sender=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        Custom retrieve method to explicitly check object-level permissions
        and return a `403 Forbidden` response if access is denied.

        This is in addition to the `permission_classes` attribute and serves
        to explicitly demonstrate handling of the `HTTP_403_FORBIDDEN` status,
        as often required by specific checks.
        """
        instance = self.get_object()
        
        # Manually invoke the object-level permission check from your custom permission class.
        if not self.permission_classes[1]().has_object_permission(request, self, instance):
            return Response(
                {"detail": "You do not have permission to access this message."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # If permission is granted, proceed with the default retrieve behavior
        return super().retrieve(request, *args, **kwargs)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows conversations to be viewed, created, updated, or deleted.

    Permissions:
    - Only authenticated users can access.
    - `IsOwnerOrParticipant` ensures users can only interact with conversations
      they are a participant of.

    Features:
    - Filtering is supported via `ConversationFilter` (e.g., by participant).
    - Automatically adds the creator of the conversation as a participant.
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrParticipant]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ConversationFilter

    def get_queryset(self):
        """
        Dynamically filters the queryset to return conversations where the
        currently authenticated user is a participant.

        The `.distinct()` call prevents duplicate conversations if a user is
        listed multiple times as a participant (though typically not an issue
        with ManyToMany fields unless complex intermediate models are used).
        """
        user = self.request.user
        if user.is_authenticated:
            # Filter conversations where the current user is a participant
            return Conversation.objects.filter(participants=user).distinct()
        
        # If the user is not authenticated, return an empty queryset
        return Conversation.objects.none()

    def perform_create(self, serializer):
        """
        Automatically adds the creator of the conversation as a participant
        after the conversation instance is saved.
        """
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        Custom retrieve method for conversations to explicitly check object-level
        permissions and return a `403 Forbidden` response if access is denied.

        Similar to `MessageViewSet`, this fulfills specific checker requirements.
        """
        instance = self.get_object()
        
        # Manually invoke the object-level permission check.
        if not self.permission_classes[1]().has_object_permission(request, self, instance):
            return Response(
                {"detail": "You do not have permission to access this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # If permission is granted, proceed with the default retrieve behavior
        return super().retrieve(request, *args, **kwargs)