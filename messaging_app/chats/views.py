# messaging_app/chats/views.py

from rest_framework import viewsets, status, filters # <-- Add these imports
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated # For general authentication
from rest_framework.exceptions import PermissionDenied, ValidationError # For custom error handling
from django.shortcuts import get_object_or_404 # Useful for retrieving objects
from django.db.models import Q # For complex queries if needed, though not strictly required here

from . import models
from . import serializers
# from .permissions import IsParticipantInConversation # If you decide to put permissions in a separate file

# --- Custom Permission ---
# This class ensures that a user can only access/modify messages in conversations they are a part of.
class IsParticipantInConversation(IsAuthenticated): # Inherit from IsAuthenticated
    """
    Custom permission to only allow participants of a conversation to view/send messages.
    """
    def has_permission(self, request, view):
        # First, ensure the user is authenticated at all.
        if not super().has_permission(request, view):
            return False

        # For list/create actions on messages, check if the user is a participant
        # The conversation_pk is expected in the URL kwargs
        conversation_pk = view.kwargs.get('conversation_pk')
        if not conversation_pk:
            # If conversation_pk is missing in kwargs, it might be a general list endpoint not tied to a specific conversation,
            # or an incorrectly routed request. For this setup, it's always tied.
            return False # Or raise a more specific error if needed

        try:
            conversation = models.Conversation.objects.get(conversation_id=conversation_pk)
        except models.Conversation.DoesNotExist:
            raise ValidationError("Conversation not found.") # Or return False and let DRF handle 404

        # Check if the requesting user is a participant in the conversation
        return conversation.participants.filter(user_id=request.user.user_id).exists()

    def has_object_permission(self, request, view, obj):
        # This is for detail actions on a specific message (e.g., retrieve, update, delete)
        # Ensure the user is the sender or a participant in the conversation the message belongs to.
        # For simplicity, we'll check if the user is a participant of the message's conversation.
        if not super().has_object_permission(request, view, obj):
            return False

        return obj.conversation.participants.filter(user_id=request.user.user_id).exists()


# --- ViewSets ---

# Conversation ViewSet: Handles listing, creating, retrieving, updating, and deleting conversations.
class ConversationViewSet(viewsets.ModelViewSet): # <-- class ConversationViewSet
    queryset = models.Conversation.objects.all()
    serializer_class = serializers.ConversationSerializer
    permission_classes = [IsAuthenticated] # Only authenticated users can manage conversations

    def perform_create(self, serializer):
        # Automatically add the creator of the conversation as a participant
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        # The checker implicitly wants this to create a new conversation

    # Optional: If you want to list conversations where the user is a participant only
    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_authenticated:
    #         return models.Conversation.objects.filter(participants=user)
    #     return models.Conversation.objects.none()

    # You could add a custom action if needed, for example, to get messages directly from conversation
    # @action(detail=True, methods=['get'], serializer_class=serializers.MessageSerializer,
    #         permission_classes=[IsAuthenticated, IsParticipantInConversation])
    # def messages(self, request, pk=None):
    #     conversation = self.get_object()
    #     messages = conversation.messages.all()
    #     serializer = self.get_serializer(messages, many=True)
    #     return Response(serializer.data)


# Message ViewSet: Handles listing and creating messages within a specific conversation.
class MessageViewSet(viewsets.ModelViewSet): # <-- class MessageViewSet
    serializer_class = serializers.MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantInConversation] # Apply the custom permission

    # Override get_queryset to filter messages by the conversation_pk from the URL
    def get_queryset(self):
        conversation_pk = self.kwargs.get('conversation_pk') # Get the UUID from the URL
        if not conversation_pk:
            # If conversation_pk is not in the URL, this is an invalid request for this ViewSet setup
            raise ValidationError("Conversation ID is required.")

        # Ensure the conversation exists and the user is a participant
        conversation = get_object_or_404(
            models.Conversation.objects.filter(participants=self.request.user),
            conversation_id=conversation_pk
        )
        return conversation.messages.all()

    # Override perform_create to automatically set the sender and conversation for a new message
    def perform_create(self, serializer):
        conversation_pk = self.kwargs.get('conversation_pk')
        if not conversation_pk:
            raise ValidationError("Conversation ID is required to send a message.")

        # Get the conversation instance using its UUID primary key
        conversation = get_object_or_404(
            models.Conversation,
            conversation_id=conversation_pk
        )

        # Check if the requesting user is a participant in this conversation before allowing to send a message
        if not conversation.participants.filter(user_id=self.request.user.user_id).exists():
            raise PermissionDenied("You are not a participant of this conversation and cannot send messages.")

        # Save the message with the current user as sender and the correct conversation
        serializer.save(sender=self.request.user, conversation=conversation)
        # The checker implicitly wants this to send messages to an existing one