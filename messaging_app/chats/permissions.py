# alx-backend-python/messaging_app/chats/permissions.py

from rest_framework import permissions

class IsOwnerOrParticipant(permissions.BasePermission):
    """
    Custom permission to only allow owners (senders) or participants
    of an object (Message/Conversation) to view, edit, or delete it.
    """
    def has_object_permission(self, request, view, obj):
        # Allow read access (GET, HEAD, OPTIONS) if the user is authenticated.
        # This covers viewing lists and details.
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # For write access (PUT, PATCH, DELETE), ensure the user is the owner/sender/participant.
        # Adapt this based on your actual Message and Conversation models.

        # --- For Message Model ---
        # If Message has a 'sender' ForeignKey to User
        if hasattr(obj, 'sender') and obj.sender == request.user:
            return True

        # --- For Conversation Model ---
        # If Conversation has a ManyToManyField 'participants'
        if hasattr(obj, 'participants'):
            # Check if the requesting user is one of the participants
            return request.user in obj.participants.all()

        # Fallback if no specific ownership/participation field is found
        # Or if your model has a generic 'owner' field
        if hasattr(obj, 'owner') and obj.owner == request.user:
            return True

        return False