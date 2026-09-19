from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

User = get_user_model()


class UserViewsTestCase(TestCase):
    """Test cases for user-related views (signup, profile, password change)."""

    def setUp(self):
        self.customer = User.objects.create_user(
            username="existing_customer",
            password="oldpass123",
            role=User.RoleChoices.CUSTOMER,
            phone_number="09123456789",
        )

    # ========== Signup Tests ==========

    def test_signup_page_loads(self):
        """Test that signup page loads successfully."""
        response = self.client.get(reverse("users:signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")

    def test_signup_success_customer(self):
        """Test successful signup for a customer."""
        data = {
            "username": "newcustomer",
            "email": "new@example.com",
            "password1": "newpass123",
            "password2": "newpass123",
        }
        response = self.client.post(reverse("users:signup"), data)
        self.assertRedirects(response, reverse("customer_dashboard"))

        user = User.objects.get(username="newcustomer")
        self.assertEqual(user.role, User.RoleChoices.CUSTOMER)
        self.assertTrue(user.is_authenticated)

    def test_signup_password_mismatch(self):
        """Test signup fails when passwords don't match."""
        data = {
            "username": "newcustomer",
            "email": "new@example.com",
            "password1": "pass123",
            "password2": "pass456",
        }
        response = self.client.post(reverse("users:signup"), data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("رمز عبور" in str(m) for m in messages))
        self.assertFalse(User.objects.filter(username="newcustomer").exists())

    def test_signup_duplicate_username(self):
        """Test signup fails with an already used username."""
        data = {
            "username": "existing_customer",
            "email": "new@example.com",
            "password1": "newpass123",
            "password2": "newpass123",
        }
        response = self.client.post(reverse("users:signup"), data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("نام کاربری" in str(m) for m in messages))

    # ========== Provider Signup Tests ==========

    def test_provider_signup_page_loads(self):
        """Test provider signup page loads successfully."""
        response = self.client.get(reverse("users:signup_provider"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup_provider.html")

    def test_provider_signup_success(self):
        """Test successful signup for a provider."""
        data = {
            "username": "newprovider",
            "email": "provider@example.com",
            "password1": "newpass123",
            "password2": "newpass123",
            "phone_number": "09123456789",
        }
        response = self.client.post(reverse("users:signup_provider"), data)
        self.assertRedirects(response, reverse("provider_dashboard"))

        user = User.objects.get(username="newprovider")
        self.assertEqual(user.role, User.RoleChoices.PROVIDER)
        self.assertEqual(user.phone_number, "09123456789")

    # ========== Profile Edit Tests ==========

    def test_profile_edit_page_requires_login(self):
        """Test profile edit page redirects unauthenticated users."""
        response = self.client.get(reverse("users:profile_edit"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_profile_edit_success(self):
        """Test editing user profile successfully."""
        self.client.login(username="existing_customer", password="oldpass123")
        data = {
            "username": "updated_name",
            "email": "newemail@example.com",
            "phone_number": "09198765432",
        }
        response = self.client.post(reverse("users:profile_edit"), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success

        self.customer.refresh_from_db()
        self.assertEqual(self.customer.username, "updated_name")
        self.assertEqual(self.customer.email, "newemail@example.com")
        self.assertEqual(self.customer.phone_number, "09198765432")

    def test_profile_edit_duplicate_username(self):
        """Test profile edit fails with an already used username."""
        User.objects.create_user(username="other_user", password="pass")
        self.client.login(username="existing_customer", password="oldpass123")

        data = {
            "username": "other_user",
            "email": "test@example.com",
            "phone_number": "09123456789",
        }
        response = self.client.post(reverse("users:profile_edit"), data)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("نام کاربری" in str(m) for m in messages))

    # ========== Password Change Tests ==========

    def test_password_change_page_requires_login(self):
        """Test password change page redirects unauthenticated users."""
        response = self.client.get(reverse("users:password_change"))
        self.assertEqual(response.status_code, 302)

    def test_password_change_success(self):
        """Test changing password successfully."""
        self.client.login(username="existing_customer", password="oldpass123")
        data = {
            "old_password": "oldpass123",
            "new_password1": "newpass456",
            "new_password2": "newpass456",
        }
        response = self.client.post(reverse("users:password_change"), data)
        self.assertRedirects(response, reverse("users:password_change_done"))

        # Verify new password works
        self.client.logout()
        self.client.login(username="existing_customer", password="newpass456")
        self.assertTrue(self.client.session.items())
