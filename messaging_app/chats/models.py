import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone


# Custom Manager for User (Optional but good practice for AbstractUser extensions)
class CustomUserManager(BaseUserManager):
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


# User Model (Extension of AbstractUser)
class User(AbstractUser):
    USER_ROLES = (
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    )

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Inherits username, first_name, last_name, email from AbstractUser
    # We will override email to be unique and required
    email = models.EmailField(unique=True, null=False, blank=False)
    # password_hash is handled by AbstractUser's password field

    phone_number = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='guest', null=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False) # Use timezone.now for consistency

    # Remove username field if you want to use email as unique identifier for login
    # If you keep username, ensure it's not the primary login method unless desired.
    # For simplicity and alignment with 'email (VARCHAR, UNIQUE, NOT NULL)', let's remove username unique constraint
    username = None # Set username to None to make email the unique identifier for auth
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role'] # Fields prompted when creating a superuser

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        # Ensure proper table name if you need to override default Django naming
        # db_table = 'user_profiles' # Example
        pass


# Conversation Model
class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Many-to-many relationship with User for participants
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"Conversation {self.conversation_id} ({self.participants.count()} participants)"

    class Meta:
        # Ensure proper table name if you need to override default Django naming
        # db_table = 'conversations' # Example
        pass


# Message Model
class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField(null=False, blank=False)
    sent_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"Message {self.message_id} from {self.sender.email} in {self.conversation.conversation_id}"

    class Meta:
        # Ensure proper table name if you need to override default Django naming
        # db_table = 'messages' # Example
        ordering = ['sent_at'] # Order messages by time sent