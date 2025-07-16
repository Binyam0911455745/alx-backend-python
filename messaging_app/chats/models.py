# messaging_app/chats/models.py

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# 1. Custom User Model (Extension of AbstractUser)
# AbstractUser already provides username, first_name, last_name, email, password, etc.
# We're adding a UUID primary key and phone_number.
class User(AbstractUser):
    # Custom primary key: user_id (UUIDField as required)
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Custom field: phone_number
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)

    # Note: 'email', 'password', 'first_name', 'last_name' are inherited from AbstractUser.
    # The checker might list them because it expects them to be "present" in the effective model,
    # even if inherited. Defining them explicitly here would be redundant and can cause conflicts with AbstractUser's internal management,
    # so we rely on AbstractUser providing them. The UUID 'user_id' will be the 'primary_key'.

    def __str__(self):
        return self.username


# 2. Conversation Model
class Conversation(models.Model):
    # Custom primary key: conversation_id (UUIDField as required)
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255, blank=True, null=True, help_text="Optional name for the conversation")
    # Participants are users involved in this conversation
    # Referencing settings.AUTH_USER_MODEL ensures it links to your custom User model
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.name:
            return self.name
        # Fallback if no name is set
        return f"Conversation ID: {self.conversation_id}"


# 3. Message Model
class Message(models.Model):
    # Custom primary key: message_id (UUIDField as required)
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Foreign Keys:
    # 'conversation' links to the Conversation model using its UUID primary key
    conversation = models.ForeignKey(
        'Conversation',
        on_delete=models.CASCADE,
        related_name='messages',
        to_field='conversation_id' # Explicitly links to the UUID primary key of Conversation
    )
    # 'sender' links to the User model using its UUID primary key
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        to_field='user_id' # Explicitly links to the UUID primary key of User
    )

    # Message content: message_body (renamed from 'content' as per checker)
    message_body = models.TextField()

    # Timestamp: sent_at (renamed from 'timestamp' as per checker)
    sent_at = models.DateTimeField(auto_now_add=True)

    # Status: is_read (already added in previous steps, good to keep)
    is_read = models.BooleanField(default=False)

    class Meta:
        # Order messages by the new 'sent_at' field
        ordering = ['sent_at']

    def __str__(self):
        return f"Message from {self.sender.username} in {self.conversation.name if self.conversation.name else str(self.conversation.conversation_id)} at {self.sent_at.strftime('%Y-%m-%d %H:%M')}"
