# Django-signals_orm-0x04/messaging/managers.py

from django.db import models
from django.db.models import F # Needed for MessageManager if it uses F objects
from django.contrib.auth import get_user_model # Needed if managers reference User directly

User = get_user_model()

class MessageManager(models.Manager):
    # Ensure your get_threaded_conversation and get_all_descendants methods are here
    def get_threaded_conversation(self, root_message_id):
        """
        Fetches a root message and all its descendants (replies, replies of replies, etc.)
        using a custom recursive approach.
        """
        try:
            # Use self.model instead of Message directly for manager methods
            root_message = self.select_related('sender', 'receiver').get(id=root_message_id)
        except self.model.DoesNotExist:
            return None
        return root_message

    def get_all_descendants(self, root_message_id):
        """
        Returns a QuerySet of all descendants (replies, replies of replies) for a given message.
        """
        message_ids = {root_message_id}
        current_level_ids = {root_message_id}

        while True:
            # self.filter refers to the Message model it's attached to
            new_replies = self.filter(parent_message_id__in=current_level_ids).values_list('id', flat=True)
            new_replies = set(new_replies) - message_ids
            if not new_replies:
                break
            message_ids.update(new_replies)
            current_level_ids = new_replies

        return self.filter(id__in=message_ids).select_related(
            'sender', 'receiver', 'parent_message'
        ).prefetch_related(
            'history'
        ).order_by('timestamp')


class UnreadMessagesManager(models.Manager):
    def unread_for_user(self, user):
        """
        Filters messages that are unread and received by the specified user.
        """
        return self.filter(receiver=user, is_read=False)