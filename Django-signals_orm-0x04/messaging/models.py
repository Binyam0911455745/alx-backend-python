# Django-signals_orm-0x04/messaging/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import F # Keep F object for database expressions if used elsewhere
from .managers import MessageManager, UnreadMessagesManager

User = get_user_model()

class MessageManager(models.Manager):
    def get_threaded_conversation(self, root_message_id):
        # ... (your existing implementation) ...
        pass # Keep your actual implementation

    def get_all_descendants(self, root_message_id):
        # ... (your existing implementation) ...
        pass # Keep your actual implementation


# NEW: Custom Manager for Unread Messages
class UnreadMessagesManager(models.Manager):
    def unread_for_user(self, user):
        """
        Filters messages that are unread and received by the specified user.
        """
        return self.filter(receiver=user, is_read=False)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False) # Indicates if the message has been edited
    
    # ADD THIS FIELD: Self-referential ForeignKey for replies
    parent_message = models.ForeignKey(
        'self', # Refers to the Message model itself
        on_delete=models.SET_NULL, # If the parent message is deleted, set this to NULL
        null=True,                # Allows the field to be NULL (top-level messages have no parent)
        blank=True,               # Allows the field to be blank in forms/admin
        related_name='replies'    # Reverse relation: message.replies will get all its children
    )
    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}: {self.content[:50]}..."
    def get_direct_replies(self):
        return self.replies.all().order_by('timestamp')

    def get_all_threaded_replies(self):
        # This calls a method on the 'objects' manager, which is MessageManager
        return Message.objects.get_all_descendants(self.id)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.content[:50]}..."
    #def get_direct_replies(self):
     #   return self.replies.all().order_by('timestamp')

    #def get_all_threaded_replies(self):
     #   return Message.objects.get_all_descendants(self.id)

class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    # ADD THIS NEW FIELD:
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='message_history_edits')

    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = "Message Histories"

    def __str__(self):
        return f"History for Message {self.message.id} (Edited at {self.edited_at.strftime('%Y-%m-%d %H:%M')})"
