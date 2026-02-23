from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class AuthTests(APITestCase):

    def setUp(self):
        self.register_url = reverse("account:register")
        self.login_url = reverse("account:login")
        self.refresh_url = reverse("account:refresh")

        self.user_data = {
            "username": "amir",
            "password": "strongpass123",
            "confirm_password": "strongpass123"
        }

        self.user = User.objects.create_user(
            username="existing_user",
            password="testpass123"
        )

    def test_register_success(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username=self.user_data['username']).exists())

    def test_register_password_mismatch(self):
        data = self.user_data.copy()
        data["confirm_password"] = "wrongpass"

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        data = {
            "username": "existing_user",
            "password": "12345678",
            "confirm_password": "12345678"
        }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        response = self.client.post(self.register_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        response = self.client.post(self.login_url, {
            "username": "existing_user",
            "password": "testpass123"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)

    def test_login_wrong_password(self):
        response = self.client.post(self.login_url, {
            "username": "existing_user",
            "password": "wrongpass"
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_not_found(self):
        response = self.client.post(self.login_url, {
            "username": "unknown",
            "password": "123456"
        })

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_inactive_user(self):
        inactive_user = User.objects.create_user(
            username="inactive",
            password="pass123",
            is_active=False
        )

        response = self.client.post(self.login_url, {
            "username": "inactive",
            "password": "pass123"
        })

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_refresh_token_success(self):
        refresh = RefreshToken.for_user(self.user)

        response = self.client.post(self.refresh_url, {
            "refresh": str(refresh)
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_token_invalid(self):
        response = self.client.post(self.refresh_url, {
            "refresh": "invalidtoken"
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)