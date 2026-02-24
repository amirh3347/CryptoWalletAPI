from decimal import Decimal

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from wallet.models import Wallet


User = get_user_model()


class WalletAPITestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")

        self.wallet_url = reverse("wallet:wallet-list-create")

        self.wallet1 = Wallet.objects.create(user=self.user1, currency="USD", balance=Decimal("100.00"))
        self.wallet2 = Wallet.objects.create(user=self.user1, currency="EUR", balance=Decimal("50.00"))

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_list_wallets_authenticated_user(self):
        self.authenticate(self.user1)
        response = self.client.get(self.wallet_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        currencies = [w["currency"] for w in response.data]
        self.assertIn("USD", currencies)
        self.assertIn("EUR", currencies)

    def test_list_wallets_other_user_no_access(self):
        self.authenticate(self.user2)
        response = self.client.get(self.wallet_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_wallet_success(self):
        self.authenticate(self.user1)
        payload = {"currency": "IRR"}
        response = self.client.post(self.wallet_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["currency"], "IRR")
        self.assertEqual(response.data["balance"], "0.0000")
        self.assertIsNotNone(response.data["wallet_address"])

    def test_create_wallet_duplicate_currency(self):
        self.authenticate(self.user1)
        payload = {"currency": "USD"}
        response = self.client.post(self.wallet_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You already have a wallet with this currency.", str(response.data))

    def test_create_wallet_another_user_same_currency(self):
        self.authenticate(self.user2)
        payload = {"currency": "USD"}
        response = self.client.post(self.wallet_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["currency"], "USD")

    def test_balance_never_negative(self):
        self.authenticate(self.user1)
        wallet = Wallet.objects.create(user=self.user1, currency="IRR", balance=Decimal("0.00"))
        wallet.balance = Decimal("-100.00")
        with self.assertRaises(Exception):
            wallet.save()

    def test_unauthenticated_access(self):
        response = self.client.get(self.wallet_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post(self.wallet_url, {"currency": "USD"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)