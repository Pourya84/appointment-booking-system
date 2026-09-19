from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, time
from appointments.models import Schedule, ServiceType, Appointment

User = get_user_model()


class HTMLViewsTestCase(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username="view_customer", password="123", role="customer"
        )
        self.provider = User.objects.create_user(
            username="view_provider", password="123", role="provider"
        )
        self.schedule = Schedule.objects.create(
            provider=self.provider,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        self.service = ServiceType.objects.create(
            name="View Service",
            duration_minutes=30,
            price=100000,
            provider=self.provider,
        )

    def test_customer_dashboard_login_required(self):
        response = self.client.get(reverse("customer_dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_customer_dashboard_authenticated(self):
        self.client.login(username="view_customer", password="123")
        response = self.client.get(reverse("customer_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointments/customer_dashboard.html")

    def test_provider_dashboard_authenticated(self):
        self.client.login(username="view_provider", password="123")
        response = self.client.get(reverse("provider_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointments/provider_dashboard.html")

    def test_create_appointment_step1_get(self):
        self.client.login(username="view_customer", password="123")
        response = self.client.get(reverse("create_appointment_step1"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointments/create_appointment.html")

    def test_cancel_appointment_as_customer(self):
        self.client.login(username="view_customer", password="123")
        apt = Appointment.objects.create(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 16),
            time=time(10, 0),
            status="pending",
        )
        response = self.client.post(reverse("cancel_appointment", args=[apt.id]))
        self.assertRedirects(response, reverse("customer_dashboard"))
        apt.refresh_from_db()
        self.assertEqual(apt.status, "cancelled")
