from django.db import models
from django.conf import settings


class ServiceType(models.Model):
    """
    Represents a type of service offered by a provider.
    """

    name = models.CharField(max_length=100)
    duration_minutes = models.PositiveSmallIntegerField(
        help_text="Duration in minutes (e.g., 30)"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "provider"},
    )

    def __str__(self):
        return f"{self.name} - {self.duration_minutes} دقیقه - {self.price} تومان"
