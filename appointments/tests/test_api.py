from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from appointments.models import ServiceType, Schedule, Appointment
from datetime import date, time

User = get_user_model()


class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username="customer_api", password="123", role="customer"
        )
        self.provider = User.objects.create_user(
            username="provider_api", password="123", role="provider"
        )
        self.schedule = Schedule.objects.create(
            provider=self.provider,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        self.service = ServiceType.objects.create(
            name="API Service", duration_minutes=30, price=100000, provider=self.provider
        )

    def test_customer_can_create_appointment(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse("api-appointments-list")
        data = {
            "provider": self.provider.id,
            "date": "2025-06-16",
            "time": "10:00",
            "service_type": self.service.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(
            Appointment.objects.first().customer, self.customer
        )

    def test_customer_cannot_confirm_appointment(self):
        self.client.force_authenticate(user=self.customer)
        apt = Appointment.objects.create(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 16),
            time=time(11, 0),
            status="pending",
        )
        url = reverse("api-appointments-confirm", args=[apt.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_provider_can_confirm_appointment(self):
        self.client.force_authenticate(user=self.provider)
        apt = Appointment.objects.create(
            customer=self.customer,
            provider=self.provider,
            date=date(2025, 6, 16),
            time=time(11, 0),
            status="pending",
        )
        url = reverse("api-appointments-confirm", args=[apt.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        apt.refresh_from_db()
        self.assertEqual(apt.status, "confirmed")