# Django-signals_orm-0x04/messaging/tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase # Import APITestCase
from rest_framework import status
from django.db import connection # For assertNumQueries

from .models import Message, Notification, MessageHistory

User = get_user_model()

class SignalTest(TestCase):
    def setUp(self):
        # Use distinct usernames for SignalTest to avoid clashes
        self.user_s1 = User.objects.create_user(username='signal_sender', password='testpassword')
        self.user_r1 = User.objects.create_user(username='signal_receiver', password='testpassword')
        self.user_a1 = User.objects.create_user(username='signal_another', password='testpassword')

        # Setup API client for testing view
        self.client = APIClient()

    def test_notification_created_on_new_message(self):
        self.assertEqual(Notification.objects.filter(user=self.user_r1).count(), 0)
        message = Message.objects.create(
            sender=self.user_s1,
            receiver=self.user_r1,
            content="Hello from sender!"
        )
        self.assertEqual(Notification.objects.filter(user=self.user_r1).count(), 1)
        notification = Notification.objects.get(user=self.user_r1)
        # Assuming notification.message is a ForeignKey to Message
        self.assertEqual(notification.message, message)
        # Assuming notification.content stores details like "from {sender_username}"
        self.assertIn(self.user_s1.username, notification.content)
        self.assertFalse(notification.is_read)
        self.assertFalse(message.edited)

    def test_no_notification_on_message_update(self):
        message = Message.objects.create(
            sender=self.user_s1,
            receiver=self.user_r1,
            content="Initial message."
        )
        initial_notification_count = Notification.objects.filter(user=self.user_r1).count()
        self.assertEqual(initial_notification_count, 1) # A notification should be created on initial message save

        message.content = "Updated content."
        message.save()

        # Notification count should not change if signal correctly prevents new notifications on update
        self.assertEqual(Notification.objects.filter(user=self.user_r1).count(), initial_notification_count)

    def test_notification_content_accuracy(self):
        # Create a message from user_a1 to user_s1
        message = Message.objects.create(
            sender=self.user_a1,
            receiver=self.user_s1,
            content="Important notice!"
        )
        # We're expecting a notification for user_s1 (the receiver) about the message from user_a1
        notification = Notification.objects.get(user=self.user_s1, message__content__contains="Important notice!")
        self.assertIn(self.user_a1.username, notification.content)
        self.assertIn("new message", notification.content)


    def test_message_edit_history_and_edited_flag(self):
        message = Message.objects.create(
            sender=self.user_s1,
            receiver=self.user_r1,
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
        history_entry = MessageHistory.objects.get(message=message) # There should only be one for now
        self.assertEqual(history_entry.old_content, old_content)

        second_old_content = new_content
        message.content = "This is the second edit."
        message.save()

        message.refresh_from_db()
        self.assertTrue(message.edited)
        self.assertEqual(MessageHistory.objects.filter(message=message).count(), 2)

        # Get the newest history entry (assuming order_by('-edited_at') in your MessageHistory model/query)
        # Or you might need to order by pk if you don't have edited_at
        newest_history = MessageHistory.objects.filter(message=message).order_by('-edited_at').first()
        self.assertEqual(newest_history.old_content, second_old_content)

    def test_message_save_without_content_change(self):
        message = Message.objects.create(
            sender=self.user_s1,
            receiver=self.user_r1,
            content="Original content."
        )
        # After initial creation, edited should be false, no history
        self.assertFalse(message.edited)
        self.assertEqual(MessageHistory.objects.filter(message=message).count(), 0)

        # Save without changing content
        message.save()

        message.refresh_from_db()
        # Edited flag should still be false
        self.assertFalse(message.edited)
        # No new history entry should be created
        self.assertEqual(MessageHistory.objects.filter(message=message).count(), 0)

        # Now change content and save, verify history is created and flag is set
        message.content = "Changed content."
        message.save()
        message.refresh_from_db()
        self.assertTrue(message.edited)
        self.assertEqual(MessageHistory.objects.filter(message=message).count(), 1)


    def test_user_deletion_cleans_up_data(self):
        """
        Test that deleting a user triggers post_delete signal to clean up
        associated messages, notifications, and message histories.
        """
        # Create a user to delete with a unique name for this test
        user_to_delete = User.objects.create_user(username='test_user_to_delete', password='deletepass')
        other_user = self.user_a1 # Use an existing user from setUp, not being deleted
        another_unrelated_user = self.user_r1 # A third user for truly independent data

        # Store the ID of the user to delete for post-deletion assertions
        user_to_delete_id = user_to_delete.id

        # Create data associated with user_to_delete
        msg1_sent_by_deleted = Message.objects.create(sender=user_to_delete, receiver=other_user, content="Msg 1 from test_user_to_delete")
        msg2_sent_by_deleted = Message.objects.create(sender=user_to_delete, receiver=other_user, content="Msg 2 from test_user_to_delete")
        msg3_received_by_deleted = Message.objects.create(sender=other_user, receiver=user_to_delete, content="Msg 3 to test_user_to_delete")
        msg4_received_by_deleted = Message.objects.create(sender=other_user, receiver=user_to_delete, content="Msg 4 to test_user_to_delete")

        # Edit msg1 and msg3 to create history
        msg1_sent_by_deleted.content = "Msg 1 edited"
        msg1_sent_by_deleted.save()
        msg3_received_by_deleted.content = "Msg 3 edited"
        msg3_received_by_deleted.save()

        # Notifications for 'test_user_to_delete' (some via messages, some potentially direct)
        Notification.objects.create(user=user_to_delete, message=msg3_received_by_deleted, content="Notif for msg3")
        Notification.objects.create(user=user_to_delete, message=None, content="Direct notif to deleted user")

        # Notification for 'other_user' about a message *from* the deleted user (should be deleted)
        # This notification's 'message' FK should cascade delete when msg1_sent_by_deleted is deleted
        Notification.objects.create(user=other_user, message=msg1_sent_by_deleted, content="Notif for msg1 (other user)")

        # NEW: Create a message and notification that are entirely unrelated to 'user_to_delete'
        # This is what should definitively NOT be deleted
        independent_message = Message.objects.create(sender=other_user, receiver=another_unrelated_user, content="Independent message.")
        independent_notification = Notification.objects.create(user=another_unrelated_user, message=independent_message, content="Independent notif.")


        # --- Assert initial counts ---
        initial_user_count = User.objects.count()
        self.assertTrue(User.objects.filter(username='test_user_to_delete').exists())

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
        response = self.client.delete(reverse('delete-my-account')) # Make sure this URL name matches your urls.py
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # --- Assert final counts ---
        self.assertFalse(User.objects.filter(username='test_user_to_delete').exists())
        self.assertEqual(User.objects.count(), initial_user_count - 1)

        # All messages sent by or received by the deleted user should be gone
        self.assertEqual(Message.objects.filter(sender_id=user_to_delete_id).count(), 0)
        self.assertEqual(Message.objects.filter(receiver_id=user_to_delete_id).count(), 0)

        # All notifications for the deleted user (user FK) should be gone
        self.assertEqual(Notification.objects.filter(user_id=user_to_delete_id).count(), 0)

class UnreadMessagesManagerTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='reader', password='password1')
        self.user2 = User.objects.create_user(username='sender', password='password2')
        self.user3 = User.objects.create_user(username='other_user', password='password3')

        # Messages to user1 (reader)
        self.unread_msg1 = Message.objects.create(sender=self.user2, receiver=self.user1, content="Hello unread 1", is_read=False)
        self.unread_msg2 = Message.objects.create(sender=self.user3, receiver=self.user1, content="Hello unread 2", is_read=False)
        self.read_msg1 = Message.objects.create(sender=self.user2, receiver=self.user1, content="Hello read 1", is_read=True)

        # Message not for user1
        self.msg_for_other = Message.objects.create(sender=self.user1, receiver=self.user3, content="Hello other", is_read=False)

        self.client.force_authenticate(user=self.user1)

    def test_unread_messages_for_user_manager_method(self):
        """
        Test the custom manager method to filter unread messages.
        """
        unread_messages = Message.unread_messages.unread_for_user(self.user1)
        self.assertEqual(unread_messages.count(), 2)
        self.assertIn(self.unread_msg1, unread_messages)
        self.assertIn(self.unread_msg2, unread_messages)
        self.assertNotIn(self.read_msg1, unread_messages)
        self.assertNotIn(self.msg_for_other, unread_messages)

    def test_unread_message_list_view(self):
        """
        Test the API endpoint for listing unread messages.
        """
        url = reverse('message-list-unread')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Check content of unread messages
        response_contents = [d['content'] for d in response.data]
        self.assertIn(self.unread_msg1.content, response_contents)
        self.assertIn(self.unread_msg2.content, response_contents)
        self.assertNotIn(self.read_msg1.content, response_contents)
        self.assertNotIn(self.msg_for_other.content, response_contents)

    def test_unread_message_list_view_query_optimization(self):
        """
        Test query optimization for UnreadMessageListView using .only() and select_related().
        """
        url = reverse('message-list-unread')

        # The exact number of queries can vary.
        # With select_related for sender/receiver and .only() for specific fields,
        # it should be 1 query for messages, and 1 query for each distinct sender/receiver if not in cache.
        # Often it's just 1 or 2 queries.
        with self.assertNumQueries(less_than=5): # Adjust this number based on your actual results.
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Verify data integrity even with .only()
            self.assertGreater(len(response.data), 0)
            self.assertIn('sender', response.data[0])
            self.assertIn('content', response.data[0])
            self.assertEqual(response.data[0]['is_read'], False)

# ... (Your existing ThreadedMessageTest and SignalTest classes) ...