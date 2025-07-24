import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.contrib.auth import get_user_model # <-- Added this line

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


# Get the custom User model after it's defined
# This is used for ForeignKey/ManyToManyField relationships to ensure correct reference
# User = get_user_model() # This line is moved below the User model definition if User is in the same file
# However, for consistency with the new changes, we typically call get_user_model()
# at the top and then use the aliased User.
# Since User is defined *in this file*, we can directly use 'User' or
# for forward references (if Message came before User), use 'chats.User' string.
# But for clarity and robustness, let's ensure models refer to the actual User class.

# Conversation Model
class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Many-to-many relationship with User for participants
    participants = models.ManyToManyField(get_user_model(), related_name='conversations') # <-- Use get_user_model() here
    created_at = models.DateTimeField(default=timezone.now, editable=False) # Keep as default=timezone.now

    def __str__(self):
        return f"Conversation {self.conversation_id} ({self.participants.count()} participants)"

    class Meta:
        # Ensure proper table name if you need to override default Django naming
        # db_table = 'conversations' # Example
        pass


# Message Model
class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Use get_user_model() for sender ForeignKey
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='sent_messages') # <-- Use get_user_model()
    # 'Conversation' in quotes for forward reference if Conversation was defined after Message
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, related_name='messages')
    content = models.TextField(null=False, blank=False) # <-- Renamed message_body to content
    timestamp = models.DateTimeField(auto_now_add=True) # <-- Renamed sent_at to timestamp and set auto_now_add

    def __str__(self):
        return f"Message {self.message_id} from {self.sender.email} in {self.conversation.conversation_id}"

    class Meta:
        # Ensure proper table name if you need to override default Django naming
        # db_table = 'messages' # Example
        ordering = ['timestamp'] # <-- Changed ordering to timestamp