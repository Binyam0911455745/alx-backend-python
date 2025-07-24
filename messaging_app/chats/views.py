# alx-backend-python/messaging_app/chats/views.py

from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404
# from django.db.models import Q # Only needed for complex OR queries, can remove if not used

from . import models
from . import serializers
from .permissions import IsOwnerOrParticipant # Import your consolidated custom permission

# --- Conversation ViewSet ---
class ConversationViewSet(viewsets.ModelViewSet):
    """
    API view to list, create, retrieve, update, and delete conversations.
    """
    queryset = models.Conversation.objects.all()
    serializer_class = serializers.ConversationSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrParticipant] # Apply your custom permission
    lookup_field = 'conversation_id' # Important: Specifies the field for lookup (e.g., in /conversations/<UUID>/)

    def get_queryset(self):
        """
        Filters conversations to only show those where the requesting user is a participant.
        """
        user = self.request.user
        if user.is_authenticated:
            # Ensure we are filtering by the custom User model's ID if user_id is the PK
            # Assuming 'participants' is a ManyToMany field to your User model
            return models.Conversation.objects.filter(participants=user).order_by('-created_at')
        return models.Conversation.objects.none() # Return empty queryset if user is not authenticated

    def perform_create(self, serializer):
        """
        Automatically adds the creator of the conversation as a participant.
        """
        conversation = serializer.save()
        # Add the current user as a participant to the newly created conversation
        conversation.participants.add(self.request.user)
        # If you want to add other participants from request data during creation,
        # you would process that here, e.g.:
        # initial_participant_ids = self.request.data.get('initial_participants', [])
        # if initial_participant_ids:
        #     other_participants = models.User.objects.filter(user_id__in=initial_participant_ids)
        #     conversation.participants.add(*other_participants)


# --- Message Views (Keeping them as Generics for Nested Resource Handling) ---
# It's generally simpler to use Generic views for nested resources
# unless you specifically use a library like drf-nested-routers.

class MessageList(generics.ListCreateAPIView):
    """
    API view to list all messages within a specific conversation
    and to create new messages in that conversation.
    """
    serializer_class = serializers.MessageSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrParticipant] # Apply your custom permission

    def get_queryset(self):
        """
        Filters messages by the conversation_pk from the URL and ensures
        the user is a participant of that conversation.
        """
        conversation_pk = self.kwargs.get('conversation_pk')
        if not conversation_pk:
            raise ValidationError("Conversation ID is required in the URL path.")

        # Ensure the conversation exists and the requesting user is a participant
        # This acts as a pre-filter for messages within a conversation the user can access
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

        # Get the conversation instance and ensure the user is a participant
        # This check is crucial before allowing message creation within that conversation.
        conversation = get_object_or_404(
            models.Conversation.objects.filter(participants=self.request.user),
            conversation_id=conversation_pk
        )

        serializer.save(sender=self.request.user, conversation=conversation)


class MessageDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific message.
    """
    queryset = models.Message.objects.all() # Initial queryset, will be filtered by get_object
    serializer_class = serializers.MessageSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrParticipant] # Apply your custom permission
    lookup_field = 'message_id' # Assuming message_id is the lookup field for individual messages

    def get_object(self):
        """
        Ensures the message belongs to the specified conversation and
        the user has permission to access it.
        """
        conversation_pk = self.kwargs.get('conversation_pk')
        message_pk = self.kwargs.get('message_id')

        if not conversation_pk or not message_pk:
            raise ValidationError("Both Conversation ID and Message ID are required in the URL path.")

        # First, ensure the conversation exists and the requesting user is a participant
        conversation = get_object_or_404(
            models.Conversation.objects.filter(participants=self.request.user),
            conversation_id=conversation_pk
        )

        # Then, retrieve the specific message within that conversation
        obj = get_object_or_404(
            models.Message,
            conversation=conversation, # Important: Filter by the conversation
            message_id=message_pk
        )

        # DRF automatically calls check_object_permissions for detail views,
        # but you can explicitly call it if you have complex pre-object retrieval logic.
        # self.check_object_permissions(self.request, obj)
        return obj

    # Removed explicit perform_update/perform_destroy checks because IsOwnerOrParticipant
    # should now handle the logic for both the sender and participants based on your model's fields.
    # The 'old file' had specific checks for 'message.sender != self.request.user', which
    # IsOwnerOrParticipant should now encapsulate.
    # If IsOwnerOrParticipant isn't strict enough (e.g., you only want the sender to edit/delete,
    # not any participant), you might need to refine IsOwnerOrParticipant or add an
    # additional, stricter permission.