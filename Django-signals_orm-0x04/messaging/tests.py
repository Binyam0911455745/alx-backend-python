#from django.test import TestCase

# Django-signals_orm_0x04/messaging/tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification

User = get_user_model()

class SignalTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='sender_user', password='testpassword')
        self.user2 = User.objects.create_user(username='receiver_user', password='testpassword')
        self.user3 = User.objects.create_user(username='another_user', password='testpassword')

    def test_notification_created_on_new_message(self):
        self.assertEqual(Notification.objects.filter(user=self.user2).count(), 0)
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello from sender!"
        )
        self.assertEqual(Notification.objects.filter(user=self.user2).count(), 1)
        notification = Notification.objects.get(user=self.user2)
        self.assertEqual(notification.message, message)
        self.assertIn(self.user1.username, notification.content)
        self.assertFalse(notification.is_read)

    def test_no_notification_on_message_update(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Initial message."
        )
        initial_notification_count = Notification.objects.filter(user=self.user2).count()
        self.assertEqual(initial_notification_count, 1)

        message.content = "Updated content."
        message.save()

        self.assertEqual(Notification.objects.filter(user=self.user2).count(), initial_notification_count)

    def test_notification_content_accuracy(self):
        message = Message.objects.create(
            sender=self.user3,
            receiver=self.user1,
            content="Important notice!"
        )
        notification = Notification.objects.get(message=message)
        self.assertIn(self.user3.username, notification.content)
        self.assertIn("new message", notification.content)
