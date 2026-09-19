from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date, time, timedelta
from appointments.models import Appointment, ServiceType, Schedule
from appointments.services import AppointmentService

User = get_user_model()


class AppointmentEdgeCasesTestCase(TestCase):
    """
    Test edge cases and boundary conditions for appointment logic.
    """

    def setUp(self):
        # Create users first
        self.customer = User.objects.create_user(
            username="customer", password="pass", role=User.RoleChoices.CUSTOMER
        )
        self.provider = User.objects.create_user(
            username="provider", password="pass", role=User.RoleChoices.PROVIDER
        )

        # Clear any existing schedules for this provider to avoid unique constraint violations
        Schedule.objects.filter(provider=self.provider).delete()

        # Create service and schedule
        self.service = ServiceType.objects.create(
            name="Test Service",
            duration_minutes=30,
            price=50000,
            provider=self.provider,
        )
        self.schedule = Schedule.objects.create(
            provider=self.provider,
            day_of_week=0,  # Monday
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

    # ========== Time Boundary Tests ==========

    def test_appointment_at_start_of_working_hours(self):
        """Test booking at exactly the start of working hours (09:00)."""
        apt = AppointmentService.create_appointment(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 16),  # Monday
            time_str="09:00",
            service_type_id=self.service.id,
        )
        self.assertEqual(apt.time, time(9, 0))
        self.assertEqual(apt.status, "pending")

    def test_appointment_at_end_of_working_hours(self):
        """Test booking at exactly the end of working hours (17:00)."""
        apt = AppointmentService.create_appointment(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 16),  # Monday
            time_str="17:00",
            service_type_id=self.service.id,
        )
        self.assertEqual(apt.time, time(17, 0))

    def test_appointment_out_of_working_hours_early(self):
        """Test booking before working hours starts (08:30)."""
        with self.assertRaises(ValidationError) as cm:
            AppointmentService.create_appointment(
                customer=self.customer,
                provider=self.provider,
                date=date(2025, 6, 16),
                time_str="08:30",
                service_type_id=None,
            )
        self.assertIn("working hours", str(cm.exception).lower())

    def test_appointment_out_of_working_hours_late(self):
        """Test booking after working hours ends (18:00)."""
        with self.assertRaises(ValidationError) as cm:
            AppointmentService.create_appointment(
                customer=self.customer,
                provider=self.provider,
                date=date(2025, 6, 16),
                time_str="18:00",
                service_type_id=None,
            )
        self.assertIn("working hours", str(cm.exception).lower())

    # ========== Date Boundary Tests ==========

    def test_appointment_on_weekend(self):
        """Test booking on a day with no working hours (Sunday)."""
        # Sunday = day_of_week = 6, no schedule exists
        with self.assertRaises(ValidationError) as cm:
            AppointmentService.create_appointment(
                customer=self.customer,
                provider=self.provider,
                date=date(2025, 6, 15),  # Sunday
                time_str="10:00",
                service_type_id=None,
            )
        self.assertIn("working hours", str(cm.exception).lower())

    def test_appointment_in_past(self):
        """Test booking a date in the past (should be rejected)."""
        past_date = date.today() - timedelta(days=1)
        with self.assertRaises(ValidationError) as cm:
            AppointmentService.create_appointment(
                customer=self.customer,
                provider=self.provider,
                date=past_date,
                time_str="10:00",
                service_type_id=None,
            )
        self.assertIn("working hours", str(cm.exception).lower())

    # ========== اصلاح تست multiple schedules ==========

    def test_appointment_date_with_multiple_schedules(self):
        """Test provider with multiple schedules on different days."""
        # Clear existing schedules
        Schedule.objects.filter(provider=self.provider).delete()

        # Create schedules for Monday and Tuesday (different days)
        Schedule.objects.create(
            provider=self.provider,
            day_of_week=0,  # Monday
            start_time=time(9, 0),
            end_time=time(12, 0),
        )
        Schedule.objects.create(
            provider=self.provider,
            day_of_week=1,  # Tuesday
            start_time=time(14, 0),
            end_time=time(18, 0),
        )

        # Book on Monday
        apt_monday = AppointmentService.create_appointment(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 16),  # Monday
            time_str="10:00",
            service_type_id=None,
        )
        self.assertEqual(apt_monday.date, date(2025, 6, 16))

        # Book on Tuesday
        apt_tuesday = AppointmentService.create_appointment(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 17),  # Tuesday
            time_str="15:00",
            service_type_id=None,
        )
        self.assertEqual(apt_tuesday.date, date(2025, 6, 17))

        # Ensure gap on Monday fails (no schedule after 12)
        with self.assertRaises(ValidationError):
            AppointmentService.create_appointment(
                customer=self.customer,
                provider=self.provider,
                date=date(2025, 6, 16),
                time_str="13:00",
                service_type_id=None,
            )

    # ========== اصلاح تست notification on cancellation ==========
    def test_notification_on_cancellation(self):
        """Test that cancellation creates notifications for both customer and provider."""
        from notifications.models import Notification

        # Clear all notifications
        Notification.objects.all().delete()

        apt = AppointmentService.create_appointment(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 16),
            time_str="10:00",
            service_type_id=None,
        )
        # After creation: 1 for customer, 1 for provider
        self.assertEqual(Notification.objects.filter(user=self.customer).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.provider).count(), 1)

        AppointmentService.cancel_appointment(apt.id, self.customer)
        # After cancellation: customer gets 1 more, provider gets 1 more (because customer cancelled)
        self.assertEqual(Notification.objects.filter(user=self.customer).count(), 2)
        self.assertEqual(Notification.objects.filter(user=self.provider).count(), 2)

        cancel_notif = Notification.objects.filter(
            user=self.customer, message__icontains="cancelled"
        ).first()
        self.assertIsNotNone(cancel_notif)

    # ========== Concurrent Booking Test (Race Condition) ==========

    def test_concurrent_booking_race_condition(self):
        """
        Simulate concurrent booking attempts.
        Only one should succeed; the second should fail.
        """
        date_obj = date(2025, 6, 16)
        time_str = "10:00"

        # First booking succeeds
        apt1 = AppointmentService.create_appointment(
            customer=self.customer,
            provider=self.provider,
            date=date_obj,
            time_str=time_str,
            service_type_id=None,
        )
        self.assertIsNotNone(apt1)

        # Second booking for same time should fail
        with self.assertRaises(ValidationError) as cm:
            AppointmentService.create_appointment(
                customer=self.customer,
                provider=self.provider,
                date=date_obj,
                time_str=time_str,
                service_type_id=None,
            )
        self.assertIn("already been booked", str(cm.exception))

        # Verify only one appointment exists
        self.assertEqual(
            Appointment.objects.filter(
                provider=self.provider, date=date_obj, time=time(10, 0)
            ).count(),
            1,
        )

    # ========== Cancellation Edge Cases ==========

    def test_cancel_appointment_after_confirmation(self):
        """Test cancellation of a confirmed appointment."""
        apt = AppointmentService.create_appointment(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 16),
            time_str="10:00",
            service_type_id=None,
        )
        apt.status = "confirmed"
        apt.save()

        cancelled = AppointmentService.cancel_appointment(apt.id, self.customer)
        self.assertEqual(cancelled.status, "cancelled")

    def test_cancel_appointment_already_cancelled(self):
        """Test cancellation of an already cancelled appointment."""
        apt = AppointmentService.create_appointment(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 16),
            time_str="10:00",
            service_type_id=None,
        )
        AppointmentService.cancel_appointment(apt.id, self.customer)

        with self.assertRaises(ValidationError) as cm:
            AppointmentService.cancel_appointment(apt.id, self.customer)
        self.assertIn("cannot be cancelled", str(cm.exception))

    def test_cancel_appointment_by_other_user(self):
        """Test cancellation by a user who is not the customer or provider."""
        other_customer = User.objects.create_user(
            username="other", password="pass", role=User.RoleChoices.CUSTOMER
        )
        apt = AppointmentService.create_appointment(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 16),
            time_str="10:00",
            service_type_id=None,
        )
        with self.assertRaises(ValidationError) as cm:
            AppointmentService.cancel_appointment(apt.id, other_customer)
        self.assertIn("not allowed", str(cm.exception))

    # ========== Confirmation Edge Cases ==========

    def test_confirm_already_confirmed_appointment(self):
        """Test confirming an already confirmed appointment."""
        apt = AppointmentService.create_appointment(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 16),
            time_str="10:00",
            service_type_id=None,
        )
        AppointmentService.confirm_appointment(apt.id, self.provider)

        with self.assertRaises(ValidationError) as cm:
            AppointmentService.confirm_appointment(apt.id, self.provider)
        self.assertIn("pending", str(cm.exception))

    def test_confirm_appointment_by_customer_fails(self):
        """Test that a customer cannot confirm an appointment."""
        apt = AppointmentService.create_appointment(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 16),
            time_str="10:00",
            service_type_id=None,
        )
        with self.assertRaises(ValidationError) as cm:
            AppointmentService.confirm_appointment(apt.id, self.customer)
        self.assertIn("provider", str(cm.exception))

    # ========== Service Type Edge Cases ==========

    def test_create_appointment_without_service_type(self):
        """Test creating an appointment without a service type."""
        apt = AppointmentService.create_appointment(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 16),
            time_str="10:00",
            service_type_id=None,
        )
        self.assertIsNone(apt.service_type)

    def test_create_appointment_with_invalid_service_type(self):
        """Test creating an appointment with a service type that doesn't exist."""
        with self.assertRaises(ServiceType.DoesNotExist):
            AppointmentService.create_appointment(
                customer=self.customer,
                provider=self.provider,
                date=date(2025, 6, 16),
                time_str="10:00",
                service_type_id=999,
            )
