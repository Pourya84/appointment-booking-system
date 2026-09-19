from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Appointment(models.Model):
    """
    Represents a booking made by a customer with a provider.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled by customer"),
        ("rejected", "Rejected by provider"),
        ("completed", "Completed"),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments_as_customer",
        limit_choices_to={"role": "customer"},
        db_index=True,
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments_as_provider",
        limit_choices_to={"role": "provider"},
        db_index=True,
    )
    service_type = models.ForeignKey(
        "ServiceType",  # string reference to avoid circular import
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("provider", "date", "time")
        ordering = ["date", "time"]

    def __str__(self):
        return f"{self.customer.username} - {self.provider.username} - {self.date} {self.time}"
