# messaging_app/chats/views.py

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from . import models # Consolidated import
from . import serializers # Consolidated import

# --- Conversation Views ---
class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = serializers.ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # A user should only see conversations they are a participant in
        user = self.request.user
        return models.Conversation.objects.filter(participants=user).distinct()

    def perform_create(self, serializer):
        # When creating a conversation, ensure the creating user is a participant.
        # Handles 'participant_ids' for ManyToMany field.
        participant_ids = self.request.data.get('participant_ids', [])
        if not participant_ids:
            # If no participants specified, default to just the creator
            participant_ids = [self.request.user.id]
        elif self.request.user.id not in participant_ids:
            # Ensure the creator is always a participant
            participant_ids.append(self.request.user.id)

        # Get User instances from IDs
        participants = models.User.objects.filter(id__in=participant_ids)
        if not participants.exists():
            raise ValidationError({"participants": "No valid participants found for provided IDs."})

        serializer.save(participants=participants)


class ConversationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Conversation.objects.all()
    serializer_class = serializers.ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # A user can only retrieve/update/delete conversations they are a participant in
        user = self.request.user
        return models.Conversation.objects.filter(participants=user).distinct()

# --- Message Views ---
class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = serializers.MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter messages by specific conversation from URL parameter
        conversation_pk = self.kwargs.get('conversation_pk')
        if not conversation_pk:
            # If no conversation_pk is provided, it's an invalid request for this view
            raise ValidationError({"detail": "Conversation ID is required to list messages."})

        # Ensure the user is a participant of the conversation they are requesting messages from
        user = self.request.user
        if not models.Conversation.objects.filter(pk=conversation_pk, participants=user).exists():
            raise PermissionDenied("You do not have access to this conversation.")

        return models.Message.objects.filter(conversation__pk=conversation_pk).order_by('timestamp')

    def perform_create(self, serializer):
        # Set the sender of the message to the current authenticated user
        conversation_pk = self.kwargs.get('conversation_pk')
        if not conversation_pk:
            raise ValidationError({"detail": "Conversation ID is required to create a message."})

        try:
            conversation = models.Conversation.objects.get(pk=conversation_pk)
        except models.Conversation.DoesNotExist:
            raise ValidationError({"conversation": "Conversation with this ID does not exist."})

        # Ensure the user sending the message is a participant of the conversation
        if not conversation.participants.filter(id=self.request.user.id).exists():
            raise PermissionDenied("You are not a participant of this conversation.")

        serializer.save(sender=self.request.user, conversation=conversation)


class MessageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Message.objects.all() # Queryset for general lookup
    serializer_class = serializers.MessageSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'message_pk' # Use 'message_pk' as the URL keyword argument for the message ID

    def get_queryset(self):
        # Ensure the user can only retrieve/update/delete messages they have access to.
        # This method will apply filtering *before* the object is retrieved by lookup_field.

        user = self.request.user
        # Filter messages where the user is a participant in the associated conversation
        return models.Message.objects.filter(
            conversation__participants=user
        ).distinct()

    # You might add custom permission logic here if only the sender can delete/edit their message,
    # but the get_queryset already ensures user is a participant of the conversation.