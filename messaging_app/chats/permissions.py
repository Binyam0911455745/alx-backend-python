# alx-backend-python/messaging_app/chats/permissions.py

from rest_framework import permissions

class IsOwnerOrParticipant(permissions.BasePermission):
    """
    Custom permission to only allow owners (senders of messages, or creators/participants of conversations)
    to view, edit, or delete the respective object.

    - For read operations (GET, HEAD, OPTIONS): Allows if the user is authenticated.
    - For write operations (PUT, PATCH, DELETE):
        - If the object has a 'sender' attribute (e.g., Message), checks if the user is the sender.
        - If the object has a 'participants' ManyToMany field (e.g., Conversation), checks if the user is a participant.
        - If the object has an 'owner' attribute, checks if the user is the owner.
    """

    def has_permission(self, request, view):
        """
        Global permission check for list views (e.g., GET /conversations/, POST /conversations/).
        Ensures user is authenticated for any operation in these views.
        """
        # For list views or creation, simply ensure the user is authenticated.
        # Object-level permission will handle specific access after creation or for existing objects.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check for detail views (e.g., GET /conversations/uuid/, PUT /messages/uuid/).
        """
        # Allow read access (GET, HEAD, OPTIONS) if the user is authenticated.
        # This is a common requirement for APIs where data might be generally viewable
        # by logged-in users, but modification is restricted.
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated # Already checked by has_permission, but good for robustness

        # For write access (PUT, PATCH, DELETE), ensure the user is the owner/sender/participant.

        # --- For Message Model ---
        # If the object is a Message, check if the request.user is its sender.
        # Also check if the user is a participant of the message's conversation.
        if hasattr(obj, 'sender') and hasattr(obj, 'conversation'):
            # User must be the sender to modify/delete the message
            if obj.sender == request.user:
                return True
            # Or, for viewing/some actions, they might just need to be a participant of the conversation
            # This part depends on your exact policy. If only sender can modify, the above is enough.
            # If participants can, for example, 'archive' messages, then:
            # return request.user in obj.conversation.participants.all() # <- Add this if participants can modify messages
            # For this consolidated permission, it's safer to limit modification to sender,
            # and participation for read-only if it's not handled by SAFE_METHODS.
            # If you specifically want non-senders who are participants to edit, this logic needs refinement.

        # --- For Conversation Model ---
        # If the object is a Conversation, check if the request.user is one of its participants.
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()

        # If your model simply has a generic 'owner' field (e.g., on a UserProfile or similar)
        if hasattr(obj, 'owner') and obj.owner == request.user:
            return True

        # If none of the above conditions are met, deny access
        return False

# You can keep IsUserOwner if it's used elsewhere for simpler ownership checks
# (e.g., for a UserProfile model that has a direct ForeignKey to User).
# However, for Message and Conversation, IsOwnerOrParticipant is more appropriate.
# class IsUserOwner(permissions.BasePermission):
#     """
#     Custom permission to only allow owners of an object to access it.
#     """
#     def has_object_permission(self, request, view, obj):
#         # Assuming the object has a 'user' or 'owner' field
#         return obj.user == request.user or (hasattr(obj, 'owner') and obj.owner == request.user)