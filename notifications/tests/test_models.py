from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from notifications.models import Notification
from datetime import timedelta

User = get_user_model()


class NotificationModelTestCase(TestCase):
    """Test cases for the Notification model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="pass123", role=User.RoleChoices.CUSTOMER
        )

    def test_create_notification(self):
        """Test creating a notification."""
        notif = Notification.objects.create(
            user=self.user,
            message="Test notification message",
            related_appointment_id=1,
        )
        self.assertEqual(notif.user, self.user)
        self.assertEqual(notif.message, "Test notification message")
        self.assertFalse(notif.is_read)
        self.assertEqual(notif.related_appointment_id, 1)
        self.assertIsNotNone(notif.created_at)

    def test_str_method(self):
        """Test the __str__ method of Notification."""
        notif = Notification.objects.create(
            user=self.user,
            message="This is a very long message that should be truncated in the string representation",
        )
        # The __str__ method shows first 30 chars + "..."
        # First 30 chars of the message are: "This is a very long message th"
        expected = "testuser: This is a very long message th..."
        self.assertEqual(str(notif), expected)

    def test_notification_ordering(self):
        """Test that notifications are ordered by created_at descending."""
        # Clear existing notifications
        Notification.objects.all().delete()

        n1 = Notification.objects.create(
            user=self.user,
            message="First",
            created_at=timezone.now() - timedelta(minutes=5),
        )
        n2 = Notification.objects.create(
            user=self.user, message="Second", created_at=timezone.now()
        )
        notifications = Notification.objects.all()
        self.assertEqual(notifications[0], n2)  # Most recent first
        self.assertEqual(notifications[1], n1)
