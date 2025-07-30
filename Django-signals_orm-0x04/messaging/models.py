#from django.db import models

# Django-signals_orm_0x04/messaging/models.py

from django.db import models
from django.conf import settings

class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_messages',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_messages',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}: {self.content[:50]}..."

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notifications',
        on_delete=models.CASCADE
    )
    message = models.ForeignKey(
        Message,
        related_name='notifications',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    content = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"Notification for {self.user.username}: {self.content[:50]}..."

class MessageHistory(models.Model): # <--- NEW MODEL: To store old content versions
    """
    Stores historical versions of a Message's content when it's edited.
    """
    message = models.ForeignKey(
        Message,
        related_name='history', # Allows accessing history from Message instance: message.history.all()
        on_delete=models.CASCADE
    )
    old_content = models.TextField() # The content before the edit
    edited_at = models.DateTimeField(auto_now_add=True) # When this specific edit history was recorded

    class Meta:
        ordering = ['-edited_at'] # Newest old version first
        verbose_name = "Message History"
        verbose_name_plural = "Message Histories"

    def __str__(self):
        return f"History for Message {self.message.id} at {self.edited_at.strftime('%Y-%m-%d %H:%M')}"


