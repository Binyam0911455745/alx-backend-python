# Django-signals_orm-0x04/messaging/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.http import Http404
from django.db import models # <--- ADDED THIS IMPORT FOR models.Q

from .models import Message, MessageHistory, Notification
from .serializers import MessageDetailSerializer, MessageHistorySerializer, NotificationSerializer

User = get_user_model()

class MessageDetailWithHistoryView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve a single message with its full edit history.
    """
    queryset = Message.objects.all()
    serializer_class = MessageDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ensure users can only see messages they sent or received
        user = self.request.user
        # Correctly using models.Q for OR conditions in filtering
        return Message.objects.filter(models.Q(sender=user) | models.Q(receiver=user))

    def get_object(self):
        # Get the object and verify permissions for the specific instance
        obj = super().get_object()
        if obj.sender != self.request.user and obj.receiver != self.request.user:
            raise Http404("You do not have permission to view this message.")
        return obj


class MessageHistoryListView(generics.ListAPIView):
    """
    API endpoint to list the history of a specific message.
    """
    serializer_class = MessageHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Assuming message_pk is passed in the URL kwargs
        message_pk = self.kwargs['message_pk']
        try:
            message = Message.objects.get(pk=message_pk)
        except Message.DoesNotExist:
            raise Http404("Message not found.")

        # Ensure the requesting user is either the sender or receiver of the message
        if message.sender != self.request.user and message.receiver != self.request.user:
            raise Http404("You do not have permission to view the history of this message.")

        # Return the history entries for the specified message
        return MessageHistory.objects.filter(message=message)


class DeleteUserAccountView(generics.DestroyAPIView):
    """
    API endpoint for a user to delete their own account.
    Triggers post_delete signal on User model for associated data cleanup.
    """
    queryset = User.objects.all() # Targets all users, but get_object restricts to current user
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Ensures a user can only delete their own account by returning the
        authenticated user making the request.
        """
        return self.request.user

    def delete(self, request, *args, **kwargs):
        """
        Handles the deletion of the user's account.
        """
        user_to_delete = self.get_object() # This retrieves the current authenticated user
        username = user_to_delete.username # Store username for the response message

        # This line triggers the User's post_delete signal
        # which should clean up related messages, notifications, and history.
        user_to_delete.delete()

        return Response(
            {"detail": f"User account '{username}' and all associated data have been successfully deleted."},
            status=status.HTTP_204_NO_CONTENT
        )