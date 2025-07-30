# Django-signals_orm-0x04/messaging/tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from .models import Message, Notification, MessageHistory

User = get_user_model()

class SignalTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='sender_user', password='testpassword')
        self.user2 = User.objects.create_user(username='receiver_user', password='testpassword')
        self.user3 = User.objects.create_user(username='another_user', password='testpassword')

        # Setup API client for testing view
        self.client = APIClient()

    def test_notification_created_on_new_message(self):
        self.assertEqual(Notification.objects.filter(user=self.user2).count(), 0)
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello from sender!"
        )
        self.assertEqual(Notification.objects.filter(user=self.user2).count(), 1)
        notification = Notification.objects.get(user=self.user2) # FIX 2: Changed recipient to user
        self.assertEqual(notification.message, message)
        self.assertIn(self.user1.username, notification.content)
        self.assertFalse(notification.is_read)
        self.assertFalse(message.edited)

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
        # Create a message from user3 to user1
        message = Message.objects.create(
            sender=self.user3,
            receiver=self.user1,
            content="Important notice!"
        )
        # We're expecting a notification for user1 (the receiver) about the message from user3
        # FIX 1: Changed recipient to user, and message__contains to message__content__contains
        notification = Notification.objects.get(user=self.user1, message__content__contains="Important notice!")
        self.assertIn(self.user3.username, notification.content)
        self.assertIn("new message", notification.content)


    def test_message_edit_history_and_edited_flag(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original message content."
        )
        self.assertFalse(message.edited)
        self.assertEqual(MessageHistory.objects.filter(message=message).count(), 0)

        old_content = message.content
        new_content = "This message has been edited."
        message.content = new_content
        message.save()

        message.refresh_from_db()
        self.assertTrue(message.edited)
        self.assertEqual(MessageHistory.objects.filter(message=message).count(), 1)
        history_entry = MessageHistory.objects.get(message=message)
        self.assertEqual(history_entry.old_content, old_content)

        second_old_content = new_content
        message.content = "This is the second edit."
        message.save()

        message.refresh_from_db()
        self.assertTrue(message.edited)
        self.assertEqual(MessageHistory.objects.filter(message=message).count(), 2)

        newest_history = MessageHistory.objects.filter(message=message).first()
        self.assertEqual(newest_history.old_content, second_old_content)

    def test_message_save_without_content_change(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original content."
        )
        self.assertFalse(message.edited)
        self.assertEqual(MessageHistory.objects.filter(message=message).count(), 0)

        message.save()

        message.refresh_from_db()
        self.assertFalse(message.edited)
        self.assertEqual(MessageHistory.objects.filter(message=message).count(), 0)

        message.content = "Changed content."
        message.save()
        message.refresh_from_db()
        self.assertTrue(message.edited)
        self.assertEqual(MessageHistory.objects.filter(message=message).count(), 1)

# Django-signals_orm-0x04/messaging/tests.py

# ... (rest of the file) ...

    # Django-signals_orm-0x04/messaging/tests.py

# ... (rest of the file) ...

    def test_user_deletion_cleans_up_data(self):
        """
        Test that deleting a user triggers post_delete signal to clean up
        associated messages, notifications, and message histories.
        """
        # Create a user to delete
        user_to_delete = User.objects.create_user(username='delete_me', password='deletepass')
        other_user = self.user3 # Use an existing user not being deleted
        another_unrelated_user = self.user1 # A third user for truly independent data

        # Store the ID of the user to delete for post-deletion assertions
        user_to_delete_id = user_to_delete.id

        # Create data associated with user_to_delete
        msg1_sent_by_deleted = Message.objects.create(sender=user_to_delete, receiver=other_user, content="Msg 1 from delete_me")
        msg2_sent_by_deleted = Message.objects.create(sender=user_to_delete, receiver=other_user, content="Msg 2 from delete_me")
        msg3_received_by_deleted = Message.objects.create(sender=other_user, receiver=user_to_delete, content="Msg 3 to delete_me")
        msg4_received_by_deleted = Message.objects.create(sender=other_user, receiver=user_to_delete, content="Msg 4 to delete_me")

        # Edit msg1 and msg3 to create history
        msg1_sent_by_deleted.content = "Msg 1 edited"
        msg1_sent_by_deleted.save()
        msg3_received_by_deleted.content = "Msg 3 edited"
        msg3_received_by_deleted.save()

        # Notifications for 'delete_me' (some via messages, some potentially direct)
        Notification.objects.create(user=user_to_delete, message=msg3_received_by_deleted, content="Notif for msg3")
        Notification.objects.create(user=user_to_delete, message=None, content="Direct notif to deleted user")

        # Notification for 'other_user' about a message *from* the deleted user (should be deleted)
        Notification.objects.create(user=other_user, message=msg1_sent_by_deleted, content="Notif for msg1 (other user)")

        # NEW: Create a message and notification that are entirely unrelated to 'user_to_delete'
        # This is what should definitively NOT be deleted
        independent_message = Message.objects.create(sender=other_user, receiver=another_unrelated_user, content="Independent message.")
        independent_notification = Notification.objects.create(user=another_unrelated_user, message=independent_message, content="Independent notif.")


        # --- Assert initial counts ---
        initial_user_count = User.objects.count()
        self.assertTrue(User.objects.filter(username='delete_me').exists())

        # Count related objects before deletion
        initial_sent_messages_count = Message.objects.filter(sender=user_to_delete).count()
        initial_received_messages_count = Message.objects.filter(receiver=user_to_delete).count()
        initial_notifications_for_deleted_user_count = Notification.objects.filter(user=user_to_delete).count()
        initial_history_count_sent_msgs = MessageHistory.objects.filter(message__sender=user_to_delete).count()
        initial_history_count_rcvd_msgs = MessageHistory.objects.filter(message__receiver=user_to_delete).count()

        # Sanity check: ensure we have data
        self.assertGreater(initial_sent_messages_count, 0)
        self.assertGreater(initial_received_messages_count, 0)
        self.assertGreater(initial_notifications_for_deleted_user_count, 0)
        self.assertGreater(initial_history_count_sent_msgs, 0)
        self.assertGreater(initial_history_count_rcvd_msgs, 0)
        self.assertTrue(Notification.objects.filter(user=another_unrelated_user, message=independent_message).exists())


        # --- Perform deletion via API (logged in as the user to delete) ---
        self.client.force_authenticate(user=user_to_delete)
        response = self.client.delete(reverse('delete-my-account'))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # --- Assert final counts ---
        self.assertFalse(User.objects.filter(username='delete_me').exists())
        self.assertEqual(User.objects.count(), initial_user_count - 1)

        # All messages sent by or received by the deleted user should be gone
        self.assertEqual(Message.objects.filter(sender_id=user_to_delete_id).count(), 0)
        self.assertEqual(Message.objects.filter(receiver_id=user_to_delete_id).count(), 0)

        # All notifications for the deleted user (user FK) should be gone
        self.assertEqual(Notification.objects.filter(user_id=user_to_delete_id).count(), 0)

        # Notifications related to messages *from* or *to* the deleted user should also be gone
        # due to cascade from message deletion.
        self.assertFalse(Notification.objects.filter(message=msg1_sent_by_deleted).exists())
        self.assertFalse(Notification.objects.filter(message=msg3_received_by_deleted).exists())


        # All history entries for messages sent/received by the deleted user should be gone
        self.assertEqual(MessageHistory.objects.filter(message__sender_id=user_to_delete_id).count(), 0)
        self.assertEqual(MessageHistory.objects.filter(message__receiver_id=user_to_delete_id).count(), 0)

        # Ensure other user's truly independent data is untouched
        self.assertTrue(User.objects.filter(username=other_user.username).exists())
        self.assertTrue(User.objects.filter(username=another_unrelated_user.username).exists())
        # The independent notification should still exist
        self.assertTrue(Notification.objects.filter(user=another_unrelated_user, message=independent_message).exists())