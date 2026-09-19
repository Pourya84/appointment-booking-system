from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, time
from appointments.models import Appointment, ServiceType, Schedule
from notifications.models import Notification

User = get_user_model()


class NotificationSignalTestCase(TestCase):
    """Test cases for signals that create notifications."""

    def setUp(self):
        self.customer = User.objects.create_user(
            username="customer", password="pass", role=User.RoleChoices.CUSTOMER
        )
        self.provider = User.objects.create_user(
            username="provider", password="pass", role=User.RoleChoices.PROVIDER
        )
        self.service = ServiceType.objects.create(
            name="Test Service",
            duration_minutes=30,
            price=50000,
            provider=self.provider,
        )
        self.schedule = Schedule.objects.create(
            provider=self.provider,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

    def test_notification_created_on_appointment_creation(self):
        """Test that two notifications are created when an appointment is created."""
        from notifications.models import Notification

        # Clear existing notifications
        Notification.objects.all().delete()

        self.assertEqual(Notification.objects.count(), 0)

        apt = Appointment.objects.create(
            customer=self.customer,
            provider=self.provider,
            service_type=self.service,
            date=date(2025, 6, 16),
            time=time(10, 0),
            status="pending",
        )

        self.assertEqual(Notification.objects.count(), 2)

        # Check customer notification
        customer_notif = Notification.objects.filter(user=self.customer).first()
        self.assertIsNotNone(customer_notif)
        self.assertIn("successfully booked", customer_notif.message)
        self.assertEqual(customer_notif.related_appointment_id, apt.id)

        # Check provider notification
        provider_notif = Notification.objects.filter(user=self.provider).first()
        self.assertIsNotNone(provider_notif)
        self.assertIn("New appointment request", provider_notif.message)

    def test_no_notification_on_appointment_update(self):
        """Test that notifications are NOT created when an appointment is updated (not created)."""
        apt = Appointment.objects.create(
            customer=self.customer,
            provider=self.provider,
            service_type=self.service,
            date=date(2025, 6, 16),
            time=time(10, 0),
            status="pending",
        )
        self.assertEqual(Notification.objects.count(), 2)

        # Update the appointment (triggers post_save with created=False)
        apt.status = "confirmed"
        apt.save()
        # No new notifications should be created
        self.assertEqual(Notification.objects.count(), 2)
