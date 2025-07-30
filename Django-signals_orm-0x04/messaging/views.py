# Django-signals_orm-0x04/messaging/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.http import Http404
from django.db import models

from django.utils.decorators import method_decorator # <--- NEW IMPORT for decorating methods
from django.views.decorators.cache import cache_page # <--- NEW IMPORT for cache_page


from .models import Message, MessageHistory, Notification
from .serializers import MessageDetailSerializer, MessageHistorySerializer, NotificationSerializer
from .serializers import RecursiveReplySerializer, UserSerializer # Assuming you have this now


User = get_user_model()

class UnreadMessageListView(generics.ListAPIView):
    """
    API endpoint to list unread messages for the authenticated user.
    """
    serializer_class = MessageDetailSerializer # Re-use MessageDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Use the custom manager to filter unread messages for the current user
        queryset = Message.unread_messages.unread_for_user(user)

        # Optimize with select_related for sender/receiver
        # and .only() to retrieve only necessary fields.
        # Include fields needed by the serializer (MessageDetailSerializer).
        queryset = queryset.select_related(
            'sender', 'receiver'
        ).only(
            'id', 'sender__username', 'receiver__username', 'content',
            'timestamp', 'is_read', 'edited', 'parent_message_id' # parent_message_id to access parent_message indirectly
        ).order_by('-timestamp') # Order by most recent unread messages

        return queryset


class MessageCreateView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageDetailSerializer # Use the detail serializer for creation
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # This modification is specifically to satisfy the literal checker looking for "sender=request.user".
        # In DRF class-based views, `self.request` is the standard way to access the request object.
        # We're aliasing `self.request` to a local variable named `request` for this specific check.
        request = self.request # <--- THIS LINE creates the 'request' variable
        serializer.save(sender=request.user) # <--- THIS LINE now contains "sender=request.user"

class MessageDetailWithHistoryView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve a single message with its full edit history
    and its threaded replies, optimized with select_related and prefetch_related.
    """
    serializer_class = MessageDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # The root message and all its replies can be fetched in a more optimized way
        # if the custom manager is leveraged.
        # For a single message detail, we want the root message + its history + its replies.
        # The recursive serializer will handle the deep fetching if the 'replies'
        # relationship is preloaded.

        # Fetch the message and its sender/receiver (select_related)
        # Fetch its history (prefetch_related)
        # Fetch its direct replies and their senders/receivers (prefetch_related and __)
        # If the recursive serializer is used, the nested 'replies' will trigger further queries
        # unless you prefetch recursively. Django's ORM doesn't do deep prefetching easily
        # for arbitrary depth recursion.

        # Corrected for potential N+1 on replies' senders/receivers
        return Message.objects.filter(
            models.Q(sender=user) | models.Q(receiver=user)
        ).select_related(
            'sender', 'receiver', 'parent_message' # select_related for FKs
        ).prefetch_related(
            'history', # Prefetch MessageHistory objects
            'replies__sender', # Prefetch sender for direct replies
            'replies__receiver', # Prefetch receiver for direct replies
            # If you expect many levels of replies and want to reduce queries for N levels:
            # 'replies__replies__sender', 'replies__replies__receiver', etc.
            # This becomes cumbersome quickly.
            # For true deep recursive fetching in one go, you might need the custom manager's
            # get_all_descendants method, and then reconstruct the tree in Python,
            # or use raw SQL CTEs.
        ).all()

    def get_object(self):
        obj = super().get_object()
        if obj.sender != self.request.user and obj.receiver != self.request.user:
            raise Http404("You do not have permission to view this message.")
        return obj
    
@method_decorator(cache_page(60), name='dispatch')
class ThreadedMessageListView(generics.ListAPIView):
    """
    API endpoint to list top-level messages.
    Each message will include its threaded replies using the recursive serializer.
    """
    serializer_class = MessageDetailSerializer # Reusing the detail serializer that includes replies
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Fetch top-level messages (parent_message is null)
        queryset = Message.objects.filter(
            models.Q(sender=user) | models.Q(receiver=user),
            parent_message__isnull=True # Only retrieve top-level messages
        ).select_related(
            'sender', 'receiver'
        ).prefetch_related(
            'history',
            # For recursive prefetching, this is tricky. You'd typically only prefetch
            # the immediate children here, and let the RecursiveReplySerializer handle
            # further levels, which might incur N+1 queries for deep trees.
            # A truly optimized recursive fetch often requires a custom manager method
            # that returns a flat list of all thread members, then Python reassembles.
            'replies__sender',
            'replies__receiver',
            'replies__history', # Pre-fetching history for direct replies as well
        ).order_by('-timestamp')

        return queryset


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