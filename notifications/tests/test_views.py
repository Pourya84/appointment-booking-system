from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from notifications.models import Notification

User = get_user_model()


class NotificationViewsTestCase(TestCase):
    """Test cases for notification views."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="pass123", role=User.RoleChoices.CUSTOMER
        )
        self.notif1 = Notification.objects.create(
            user=self.user,
            message="Message 1",
            is_read=False,
        )
        self.notif2 = Notification.objects.create(
            user=self.user,
            message="Message 2",
            is_read=True,
        )

    def test_notification_list_requires_login(self):
        """Test that notification list redirects unauthenticated users."""
        response = self.client.get(reverse("notifications:notification_list"))
        self.assertEqual(response.status_code, 302)

    def test_notification_list_authenticated(self):
        """Test that authenticated users can see their notifications."""
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("notifications:notification_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notifications/list.html")
        self.assertContains(response, "Message 1")
        self.assertContains(response, "Message 2")

    def test_mark_as_read(self):
        """Test marking a notification as read."""
        self.client.login(username="testuser", password="pass123")
        url = reverse("notifications:mark_as_read", args=[self.notif1.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse("notifications:notification_list"))

        self.notif1.refresh_from_db()
        self.assertTrue(self.notif1.is_read)

    def test_mark_as_read_other_user_forbidden(self):
        """Test that users cannot mark other users' notifications as read."""
        other_user = User.objects.create_user(
            username="other", password="pass", role=User.RoleChoices.CUSTOMER
        )
        self.client.login(username="other", password="pass")
        url = reverse("notifications:mark_as_read", args=[self.notif1.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_mark_all_as_read(self):
        """Test marking all notifications as read."""
        self.client.login(username="testuser", password="pass123")
        self.assertEqual(Notification.objects.filter(user=self.user, is_read=False).count(), 1)

        response = self.client.post(reverse("notifications:mark_all_as_read"))
        self.assertRedirects(response, reverse("notifications:notification_list"))

        self.assertEqual(Notification.objects.filter(user=self.user, is_read=False).count(), 0)

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("پیام" in str(m) for m in messages))

    def test_mark_all_as_read_get_method_forbidden(self):
        """Test that GET request to mark_all_as_read is rejected."""
        self.client.login(username="testuser", password="pass123")
        response = self.client.get(reverse("notifications:mark_all_as_read"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("نامعتبر" in str(m) for m in messages))