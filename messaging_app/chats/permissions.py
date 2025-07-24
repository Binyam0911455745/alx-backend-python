# alx-backend-python/messaging_app/chats/permissions.py

from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Read-only permissions are allowed for any authenticated user.
    Assumes the model instance has an 'owner' attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        # Assuming your model has an 'owner' field linked to the user
        return obj.owner == request.user

class IsMessageSenderOrParticipant(permissions.BasePermission):
    """
    Custom permission to only allow the sender or a participant of a conversation
    to view/modify messages/conversations.
    """
    def has_object_permission(self, request, view, obj):
        # Allow read-only access to anyone who is authenticated
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # For write operations (PUT, PATCH, DELETE), ensure the user is the owner/sender
        # Adapt this logic based on your Message/Conversation model structure
        # Example: For a Message model where 'sender' is the user who sent it
        if hasattr(obj, 'sender') and obj.sender == request.user:
            return True

        # Example: For a Conversation model where 'participants' is a ManyToMany field
        if hasattr(obj, 'participants') and request.user in obj.participants.all():
            return True

        # Default to false if no specific match
        return False

# A simpler version if ownership is strictly by an 'owner' or 'user' field on the model
class IsUserOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Assuming the object has a 'user' or 'owner' field
        return obj.user == request.user or obj.owner == request.user