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
        self.assertTrue(User.objects.filter(email="ana@example.com").exists())

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user(
            username="ana@example.com",
            email="ana@example.com",
            password="12345678",
            first_name="Ana",
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
