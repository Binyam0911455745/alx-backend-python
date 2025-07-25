# chats/models.py

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q # Added for potential future filtering in views


# Custom Manager for User
class CustomUserManager(BaseUserManager):
    """
    Custom manager for the User model, providing methods for creating
    regular users and superusers with email as the unique identifier.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin') # Default for superuser

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# Custom User Model
class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser to use email as the
    primary identifier and include custom fields like UUID primary key,
    phone number, and user roles.
    """
    USER_ROLES = (
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    )

    # Use a UUID as the primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # Renamed from user_id to id for Django's default behavior
    
    # Email is unique and required for authentication
    email = models.EmailField(unique=True, null=False, blank=False)
    
    # Custom fields
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='guest', null=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    # Remove username field and set email as the USERNAME_FIELD
    username = None 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role'] # Fields prompted when creating a superuser

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        # Define a verbose name for the admin interface
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        # Optionally, set the database table name
        # db_table = 'app_users' # Example: if you want a custom table name


# Important: Always use get_user_model() when referencing the User model
# to ensure compatibility with custom user models configured in settings.py
User = get_user_model()


# Conversation Model
class Conversation(models.Model):
    """
    Represents a conversation between multiple participants.
    """
    # Using Django's default auto-incrementing 'id' for primary key
    # If you want a UUID primary key for Conversation, change `id` field:
    # conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True) # Automatically set creation time
    updated_at = models.DateTimeField(auto_now=True)     # Automatically update on save
    
    # Optional: Add a name/title for group conversations
    # name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        # Improve __str__ for clarity
        participant_names = ", ".join([p.email for p in self.participants.all()])
        return f"Conversation {self.id} with {participant_names}"

    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        # db_table = 'messaging_conversations' # Example


# Message Model
class Message(models.Model):
    """
    Represents a single message within a conversation.
    """
    # Using Django's default auto-incrementing 'id' for primary key
    # If you want a UUID primary key for Message, change `id` field:
    # message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField() # Renamed from message_body for clarity, as per your "correction"
    timestamp = models.DateTimeField(auto_now_add=True) # Automatically set when message is created

    class Meta:
        ordering = ['timestamp'] # Order messages chronologically
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        # db_table = 'conversation_messages' # Example

    def __str__(self):
        return f"Message {self.id} from {self.sender.email} in Conv {self.conversation.id}: {self.content[:50]}..."