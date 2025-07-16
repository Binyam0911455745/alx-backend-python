from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission # Import Group and Permission
from django.conf import settings # Import settings to reference AUTH_USER_MODEL

# 1. Custom User Model (Extension of AbstractUser)
# This allows you to add custom fields to your User model later if needed.
# For now, it's a minimal extension.
class User(models.Model): # Assuming this is your custom User model, if not, adjust
    # Your custom User fields here
    username = models.CharField(max_length=150, unique=True)
    # Add other fields you need for your custom user.
    # This model needs to be used if you're not using Django's default Auth user directly.
    # If you are using settings.AUTH_USER_MODEL, ensure it points to this User model or Django's default.

    def __str__(self):
        return self.username


class Conversation(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, help_text="Optional name for the conversation")
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True) # Good practice to have timestamps

    def __str__(self):
        # Show a name if available, otherwise list participants
        if self.name:
            return self.name
        return f"Conversation with {', '.join([str(p) for p in self.participants.all()])}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False) # Add this line


    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} in {self.conversation} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
