from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager


class User(AbstractUser):
    """
    Custom User model with role-based access control.
    """

    class RoleChoices(models.TextChoices):
        """
        Available roles for users in the system.
        """

        CUSTOMER = "customer", "مشتری"
        PROVIDER = "provider", "ارائه‌دهنده"
        ADMIN = "admin", "مدیر"

    role = models.CharField(
        max_length=10,
        choices=RoleChoices.choices,
        default=RoleChoices.CUSTOMER,
        help_text="User role in the system",
    )
    phone_number = models.CharField(max_length=15, blank=True)
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
