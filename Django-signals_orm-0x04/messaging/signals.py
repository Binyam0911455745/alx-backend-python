# Django-signals_orm_0x04/messaging/signals.py

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

User = get_user_model() # Get the currently active User model


@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            content=f"You have a new message from {instance.sender.username}."
        )
        print(f"Notification created for {instance.receiver.username} about message from {instance.sender.username}.")

@receiver(pre_save, sender=Message) # <--- NEW SIGNAL HANDLER
def log_message_history(sender, instance, **kwargs):
    """
    Signal receiver function to log old message content before an update.
    Also sets the 'edited' flag on the Message.
    """
    if instance.pk: # Check if the instance already exists in the database (i.e., it's an update, not a creation)
        try:
            # Retrieve the old instance from the database
            old_instance = Message.objects.get(pk=instance.pk)

            # Check if the content has actually changed
            if old_instance.content != instance.content:
                # Create a MessageHistory entry with the old content
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_instance.content
                )
                # Set the edited flag on the message
                instance.edited = True
                print(f"History logged for Message {instance.id}: Old content recorded.")
            else:
                # If content hasn't changed, ensure 'edited' remains as it was
                instance.edited = old_instance.edited

        except Message.DoesNotExist:
            # This case should ideally not happen for an existing PK, but good to handle defensively
            pass
    else:
        # This is a new message being created, so it cannot have previous history yet.
        # Ensure 'edited' is False for new messages.
        instance.edited = False

@receiver(post_delete, sender=User)
def clean_up_user_data(sender, instance, **kwargs):
    """
    Signal receiver to clean up all messages, notifications, and message histories
    associated with a user after their account is deleted.
    """
    print(f"User '{instance.username}' (ID: {instance.id}) has been deleted. Cleaning up related data...")
    user_id = instance.id # Get the ID before proceeding

    # Delete messages sent by the user
    # Use user_id for filtering
    sent_messages_count, _ = Message.objects.filter(sender_id=user_id).delete()
    print(f"   - Deleted {sent_messages_count} messages sent by user.")

    # Delete messages received by the user
    # Use user_id for filtering
    received_messages_count, _ = Message.objects.filter(receiver_id=user_id).delete()
    print(f"   - Deleted {received_messages_count} messages received by user.")

    # Delete notifications directly associated with the user
    # Use user_id for filtering
    notifications_count, _ = Notification.objects.filter(user_id=user_id).delete()
    print(f"   - Deleted {notifications_count} notifications for user.")

    # MessageHistory will largely be cleaned up via CASCADE from Message deletion.
    # The counts in the test should still confirm this.

    print(f"Cleanup for user '{instance.username}' completed.")
