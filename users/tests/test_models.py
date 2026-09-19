from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTestCase(TestCase):
    """Test cases for the custom User model."""

    def test_create_customer(self):
        """Test creating a user with CUSTOMER role."""
        user = User.objects.create_user(
            username="customer1",
            password="testpass123",
            role=User.RoleChoices.CUSTOMER
        )
        self.assertEqual(user.role, User.RoleChoices.CUSTOMER)
        self.assertEqual(user.get_role_display(), "مشتری")
        self.assertTrue(user.is_authenticated)

    def test_create_provider(self):
        """Test creating a user with PROVIDER role."""
        user = User.objects.create_user(
            username="provider1",
            password="testpass123",
            role=User.RoleChoices.PROVIDER
        )
        self.assertEqual(user.role, User.RoleChoices.PROVIDER)
        self.assertEqual(user.get_role_display(), "ارائه‌دهنده")

    def test_create_superuser(self):
        """Test creating a superuser with ADMIN role."""
        admin = User.objects.create_superuser(
            username="admin1",
            password="testpass123",
            email="admin@example.com"
        )
        self.assertEqual(admin.role, User.RoleChoices.ADMIN)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)

    def test_str_method(self):
        """Test the __str__ method of User model."""
        user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            role=User.RoleChoices.PROVIDER
        )
        self.assertEqual(str(user), "testuser (ارائه‌دهنده)")

    def test_unique_username(self):
        """Test that username must be unique."""
        User.objects.create_user(username="uniqueuser", password="pass")
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username="uniqueuser", password="pass2")