from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from users.decorators import require_role

User = get_user_model()


def dummy_view(request):
    return "OK"


class RequireRoleDecoratorTestCase(TestCase):
    """Test cases for the require_role decorator."""

    def setUp(self):
        self.factory = RequestFactory()
        self.customer = User.objects.create_user(
            username="customer", password="pass", role=User.RoleChoices.CUSTOMER
        )
        self.provider = User.objects.create_user(
            username="provider", password="pass", role=User.RoleChoices.PROVIDER
        )

    def test_allow_customer(self):
        """Test that a customer can access a view requiring customer role."""
        decorated = require_role([User.RoleChoices.CUSTOMER])(dummy_view)
        request = self.factory.get("/")
        request.user = self.customer
        result = decorated(request)
        self.assertEqual(result, "OK")

    def test_allow_provider(self):
        """Test that a provider can access a view requiring provider role."""
        decorated = require_role([User.RoleChoices.PROVIDER])(dummy_view)
        request = self.factory.get("/")
        request.user = self.provider
        result = decorated(request)
        self.assertEqual(result, "OK")

    def test_deny_customer_accessing_provider_view(self):
        """Test that a customer cannot access a provider-only view."""
        decorated = require_role([User.RoleChoices.PROVIDER])(dummy_view)
        request = self.factory.get("/")
        request.user = self.customer
        with self.assertRaises(PermissionDenied):
            decorated(request)

    def test_deny_provider_accessing_customer_view(self):
        """Test that a provider cannot access a customer-only view."""
        decorated = require_role([User.RoleChoices.CUSTOMER])(dummy_view)
        request = self.factory.get("/")
        request.user = self.provider
        with self.assertRaises(PermissionDenied):
            decorated(request)

    def test_deny_unauthenticated(self):
        """Test that unauthenticated users are denied access."""
        decorated = require_role([User.RoleChoices.CUSTOMER])(dummy_view)
        request = self.factory.get("/")
        request.user = None  # Anonymous user
        with self.assertRaises(PermissionDenied):
            decorated(request)