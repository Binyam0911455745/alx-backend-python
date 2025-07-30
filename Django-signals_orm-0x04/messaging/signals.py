# Django-signals_orm_0x04/messaging/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification

@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            content=f"You have a new message from {instance.sender.username}."
        )
        print(f"Notification created for {instance.receiver.username} about message from {instance.sender.username}.")