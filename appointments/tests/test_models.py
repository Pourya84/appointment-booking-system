from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, time
from appointments.models import ServiceType, Schedule, Appointment

User = get_user_model()


class ModelsTestCase(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username="test_customer", password="123", role="customer"
        )
        self.provider = User.objects.create_user(
            username="test_provider", password="123", role="provider"
        )
        self.service = ServiceType.objects.create(
            name="Test Service",
            duration_minutes=30,
            price=100000,
            provider=self.provider,
        )
        self.schedule = Schedule.objects.create(
            provider=self.provider,
            day_of_week=0,  # Monday
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

    def test_service_type_str(self):
        self.assertEqual(str(self.service), "Test Service - 30 دقیقه - 100000 تومان")

    def test_schedule_str(self):
        expected = f"test_provider - شنبه 09:00:00-17:00:00"
        self.assertEqual(str(self.schedule), expected)

    def test_appointment_creation(self):
        apt = Appointment.objects.create(
            customer=self.customer,
            provider=self.provider,
            service_type=self.service,
            date=date(2025, 6, 15),
            time=time(10, 0),
            status="pending",
        )
        self.assertEqual(apt.status, "pending")
        self.assertEqual(
            str(apt), f"test_customer - test_provider - 2025-06-15 10:00:00"
        )

    def test_appointment_unique_together(self):
        Appointment.objects.create(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 15),
            time=time(10, 0),
        )
        with self.assertRaises(Exception):
            Appointment.objects.create(
                customer=self.customer,
                provider=self.provider,
                date=date(2025, 6, 15),
                time=time(10, 0),
            )
