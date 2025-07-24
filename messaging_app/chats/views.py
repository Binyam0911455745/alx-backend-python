# alx-backend-python/messaging_app/chats/views.py

from rest_framework import generics, status, viewsets # <-- Add 'viewsets' here
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Q # Keep if you anticipate complex queries, otherwise can remove

from . import models
from . import serializers
from .permissions import IsOwnerOrReadOnly, IsMessageSenderOrParticipant, IsUserOwner # Import your custom permissions

# --- Conversation ViewSet ---
# This combines the functionality of ConversationList and ConversationDetail
# into a single ViewSet that works with routers.
class ConversationViewSet(viewsets.ModelViewSet): # <--- Corrected to inherit from viewsets.ModelViewSet
    """
    API view to list, create, retrieve, update, and delete conversations.
    """
    queryset = models.Conversation.objects.all()
    serializer_class = serializers.ConversationSerializer
    permission_classes = [IsAuthenticated, IsMessageSenderOrParticipant] # Apply permissions as needed
    lookup_field = 'conversation_id' # Important: Specifies the field for lookup (e.g., in /conversations/<UUID>/)

    def get_queryset(self):
        """
        Filters conversations to only show those where the requesting user is a participant.
        """
        user = self.request.user
        if user.is_authenticated:
            # Ensure we are filtering by the custom User model's ID if user_id is the PK
            return models.Conversation.objects.filter(participants=user).order_by('-created_at')
        return models.Conversation.objects.none()

    def perform_create(self, serializer):
        """
        Automatically adds the creator of the conversation as a participant.
        """
        # Save the conversation first
        conversation = serializer.save()
        # Add the current user as a participant
        conversation.participants.add(self.request.user)
        # You might want to add other initial participants based on request data here
        # For example: if 'initial_participants_ids' in self.request.data:
        #    participants = models.User.objects.filter(user_id__in=self.request.data['initial_participants_ids'])
        #    conversation.participants.add(*participants)

    def perform_destroy(self, instance):
        """
        Checks if the user has permission to delete the conversation.
        """
        # For deletion, you might want a stricter permission, e.g., only the creator
        # or an admin. If IsMessageSenderOrParticipant covers it, fine.
        # Otherwise, consider a specific permission like IsConversationCreator.
        if not instance.participants.filter(user_id=self.request.user.user_id).exists():
            raise PermissionDenied("You do not have permission to delete this conversation.")
        instance.delete()


# --- Message Views ---
# These remain as generics views because they are nested resources
# and are explicitly routed in urls.py, not through the router.

class MessageList(generics.ListCreateAPIView):
    """
    API view to list all messages within a specific conversation
    and to create new messages in that conversation.
    """
    serializer_class = serializers.MessageSerializer
    permission_classes = [IsAuthenticated, IsMessageSenderOrParticipant]

    def get_queryset(self):
        """
        Filters messages by the conversation_pk from the URL and ensures
        the user is a participant of that conversation.
        """
        conversation_pk = self.kwargs.get('conversation_pk')
        if not conversation_pk:
            raise ValidationError("Conversation ID is required.")

        # Ensure the conversation exists and the requesting user is a participant
        conversation = get_object_or_404(
            models.Conversation.objects.filter(participants=self.request.user),
            conversation_id=conversation_pk
        )
        return conversation.messages.all().order_by('timestamp') # Order messages by timestamp

    def perform_create(self, serializer):
        """
        Automatically sets the sender and conversation for a new message.
        """
        conversation_pk = self.kwargs.get('conversation_pk')
        if not conversation_pk:
            raise ValidationError("Conversation ID is required to send a message.")

        # Get the conversation instance
        conversation = get_object_or_404(
            models.Conversation,
            conversation_id=conversation_pk
        )

        # The IsMessageSenderOrParticipant permission should already handle this,
        # but a double-check here doesn't hurt for clarity or specific error messages.
        if not conversation.participants.filter(user_id=self.request.user.user_id).exists():
            raise PermissionDenied("You are not a participant of this conversation and cannot send messages.")

        serializer.save(sender=self.request.user, conversation=conversation)


class MessageDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific message.
    """
    queryset = models.Message.objects.all()
    serializer_class = serializers.MessageSerializer
    permission_classes = [IsAuthenticated, IsMessageSenderOrParticipant] # Applies to both sender and participant
    lookup_field = 'message_id' # Assuming message_id is the lookup field

    def get_object(self):
        """
        Ensures the message belongs to the specified conversation and
        the user has permission to access it.
        """
        conversation_pk = self.kwargs.get('conversation_pk')
        message_pk = self.kwargs.get('message_id') # Get the message ID from URL kwargs

        if not conversation_pk or not message_pk:
            raise ValidationError("Both Conversation ID and Message ID are required.")

        # Ensure the conversation exists and the user is a participant
        conversation = get_object_or_404(
            models.Conversation.objects.filter(participants=self.request.user),
            conversation_id=conversation_pk
        )

        # Retrieve the message belonging to this conversation
        obj = get_object_or_404(
            models.Message,
            conversation=conversation,
            message_id=message_pk
        )
        self.check_object_permissions(self.request, obj) # Explicitly check object-level permissions
        return obj

    def perform_update(self, serializer):
        """
        Ensures only the sender can update their message.
        """
        message = self.get_object()
        if message.sender != self.request.user:
            raise PermissionDenied("You can only edit your own messages.")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Ensures only the sender can delete their message.
        """
        if instance.sender != self.request.user:
            raise PermissionDenied("You can only delete your own messages.")
        instance.delete()