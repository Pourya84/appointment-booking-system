from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date, time
from appointments.models import Schedule, ServiceType
from appointments.services import AppointmentService

User = get_user_model()


class AppointmentServiceTestCase(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username="customer1", password="123", role="customer"
        )
        self.provider = User.objects.create_user(
            username="provider1", password="123", role="provider"
        )
        self.schedule = Schedule.objects.create(
            provider=self.provider,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        self.service_type = ServiceType.objects.create(
            name="Consultation",
            duration_minutes=30,
            price=50000,
            provider=self.provider,
        )

    def test_create_appointment_success(self):
        apt = AppointmentService.create_appointment(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 16),
            time_str="10:00",
            service_type_id=self.service_type.id,
        )
        self.assertEqual(apt.status, "pending")
        self.assertEqual(apt.customer, self.customer)
        self.assertEqual(apt.provider, self.provider)

    def test_create_appointment_out_of_schedule(self):
        with self.assertRaises(ValidationError) as cm:
            AppointmentService.create_appointment(
                customer=self.customer,
                provider=self.provider,
                date=date(2025, 6, 16),
                time_str="18:00",
                service_type_id=None,
            )
        error_msg = str(cm.exception)
        # Check for English error message
        self.assertIn("working hours", error_msg.lower())

    def test_create_appointment_duplicate(self):
        AppointmentService.create_appointment(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 16),
            time_str="10:00",
            service_type_id=None,
        )
        with self.assertRaises(ValidationError) as cm:
            AppointmentService.create_appointment(
                customer=self.customer,
                provider=self.provider,
                date=date(2025, 6, 16),
                time_str="10:00",
                service_type_id=None,
            )
        self.assertEqual(
            str(cm.exception),
            "['This time slot has already been booked by someone else.']",
        )

    def test_cancel_appointment_by_customer(self):
        apt = AppointmentService.create_appointment(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 16),
            time_str="11:00",
            service_type_id=None,
        )
        cancelled = AppointmentService.cancel_appointment(apt.id, self.customer)
        self.assertEqual(cancelled.status, "cancelled")

    def test_confirm_appointment_by_provider(self):
        apt = AppointmentService.create_appointment(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 16),
            time_str="11:00",
            service_type_id=None,
        )
        confirmed = AppointmentService.confirm_appointment(apt.id, self.provider)
        self.assertEqual(confirmed.status, "confirmed")

    def test_reject_appointment_by_provider(self):
        apt = AppointmentService.create_appointment(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 16),
            time_str="11:00",
            service_type_id=None,
        )
        rejected = AppointmentService.reject_appointment(apt.id, self.provider)
        self.assertEqual(rejected.status, "rejected")
