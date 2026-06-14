import uuid

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class RegisterViewTests(APITestCase):
    def test_register_creates_user(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "name": "Ana Silva",
                "email": "ana@example.com",
                "password": "12345678",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Ana Silva")
        self.assertEqual(response.data["email"], "ana@example.com")
        self.assertNotIn("password", response.data)

        user = User.objects.get(email="ana@example.com")
        self.assertIsInstance(user.id, uuid.UUID)
        self.assertEqual(user.full_name, "Ana Silva")
        self.assertNotEqual(user.password, "12345678")
        self.assertTrue(user.check_password("12345678"))

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user(
            email="ana@example.com",
            password="12345678",
            full_name="Ana",
        )

        response = self.client.post(
            "/api/auth/register/",
            {
                "name": "Ana Silva",
                "email": "ANA@example.com",
                "password": "12345678",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)


class LoginViewTests(APITestCase):
    def test_login_returns_jwt_tokens(self):
        User.objects.create_user(
            email="ana@example.com",
            password="12345678",
            full_name="Ana",
        )

        response = self.client.post(
            "/api/auth/login/",
            {
                "email": "ana@example.com",
                "password": "12345678",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertNotIn("password", response.data)

    def test_login_rejects_inactive_user(self):
        User.objects.create_user(
            email="ana@example.com",
            password="12345678",
            full_name="Ana",
            is_active=False,
        )

        response = self.client.post(
            "/api/auth/login/",
            {
                "email": "ana@example.com",
                "password": "12345678",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenRefreshViewTests(APITestCase):
    def test_refresh_token_returns_new_access_token(self):
        User.objects.create_user(
            email="ana@example.com",
            password="12345678",
            full_name="Ana",
        )

        login_response = self.client.post(
            "/api/auth/login/",
            {
                "email": "ana@example.com",
                "password": "12345678",
            },
            format="json",
        )
        refresh = login_response.data["refresh"]

        response = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": refresh},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_token_rejects_invalid_token(self):
        response = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": "invalid-token"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
