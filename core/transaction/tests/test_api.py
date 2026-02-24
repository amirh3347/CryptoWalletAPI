import uuid

from decimal import Decimal

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from wallet.models import Wallet


User = get_user_model()


class TransactionAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="amir",
            password="123456"
        )

        self.wallet = Wallet.objects.create(
            user=self.user,
            currency="USD",
            balance=Decimal("1000.0000")
        )

        self.client.force_authenticate(user=self.user)

    def test_deposit(self):
        url = reverse("transactions:deposit")

        response = self.client.post(url, {
            "wallet_address": str(self.wallet.wallet_address),
            "amount": "100.0000",
            "idempotency_key": str(uuid.uuid4())
        }, format="json")

        self.assertEqual(response.status_code, 201)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("1100.0000"))

    def test_withdraw(self):
        url = reverse("transactions:withdraw")

        response = self.client.post(url, {
            "wallet_address": str(self.wallet.wallet_address),
            "amount": "200.0000",
            "idempotency_key": str(uuid.uuid4())
        }, format="json")

        self.assertEqual(response.status_code, 201)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("800.0000"))

    def test_idempotency(self):
        url = reverse("transactions:deposit")
        key = str(uuid.uuid4())

        payload = {
            "wallet_address": str(self.wallet.wallet_address),
            "amount": "100.0000",
            "idempotency_key": key
        }

        r1 = self.client.post(url, payload, format="json")
        r2 = self.client.post(url, payload, format="json")

        self.wallet.refresh_from_db()

        self.assertEqual(r1.status_code, 201)
        self.assertEqual(r2.status_code, 201)
        self.assertEqual(self.wallet.balance, Decimal("1100.0000"))
