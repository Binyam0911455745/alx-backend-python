# Django-signals_orm-0x04/messaging/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model # Import get_user_model
from django.http import Http404 # Add Http404 for handling not found (if needed for context)


from .models import Message, MessageHistory
from .serializers import MessageDetailSerializer, MessageHistorySerializer

User = get_user_model() # <--- THIS LINE MUST BE HERE, BEFORE User is used in queryset!

# Existing Message/MessageHistory views (if any)
# ...

class MessageDetailWithHistoryView(generics.RetrieveAPIView):
    # ... (existing code for this view) ...
    pass # Keep the actual code here


class MessageHistoryListView(generics.ListAPIView):
    # ... (existing code for this view) ...
    pass # Keep the actual code here


class DeleteUserAccountView(generics.DestroyAPIView):
    """
    API endpoint for a user to delete their own account.
    Triggers post_delete signal on User model for associated data cleanup.
    """
    queryset = User.objects.all() # Correctly defined now
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Allow a user to delete only their own account
        return self.request.user

    def delete(self, request, *args, **kwargs):
        user_to_delete = self.get_object()
        username = user_to_delete.username # Store username before deletion for response
        user_to_delete.delete() # This triggers the post_delete signal on User
        return Response(
            {"detail": f"User account '{username}' and all associated data have been successfully deleted."},
            status=status.HTTP_204_NO_CONTENT
        )