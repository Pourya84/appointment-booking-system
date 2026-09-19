from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):
    """
    Custom user manager that sets default role for users.
    """

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", "customer")
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return super().create_superuser(username, email, password, **extra_fields)
