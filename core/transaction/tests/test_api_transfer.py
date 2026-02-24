import uuid

from decimal import Decimal

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

from wallet.models import Wallet


User = get_user_model()


class TransferAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="amir",
            password="123456"
        )

        self.other_user = User.objects.create_user(
            username="reza",
            password="123456"
        )

        self.wallet_from = Wallet.objects.create(
            user=self.user,
            currency="USD",
            balance=Decimal("1000.0000")
        )

        self.wallet_to = Wallet.objects.create(
            user=self.other_user,
            currency="USD",
            balance=Decimal("100.0000")
        )

        self.url = reverse("transactions:transfer")

        self.client.force_authenticate(user=self.user)

    def test_transfer_success(self):
        response = self.client.post(self.url, {
            "wallet_from_address": str(self.wallet_from.wallet_address),
            "wallet_to_address": str(self.wallet_to.wallet_address),
            "amount": "300.0000",
            "idempotency_key": str(uuid.uuid4())
        }, format="json")

        self.assertEqual(response.status_code, 201)

        self.wallet_from.refresh_from_db()
        self.wallet_to.refresh_from_db()

        self.assertEqual(self.wallet_from.balance, Decimal("700.0000"))
        self.assertEqual(self.wallet_to.balance, Decimal("400.0000"))

    def test_transfer_insufficient_balance(self):
        response = self.client.post(self.url, {
            "wallet_from_address": str(self.wallet_from.wallet_address),
            "wallet_to_address": str(self.wallet_to.wallet_address),
            "amount": "5000.0000",
            "idempotency_key": str(uuid.uuid4())
        }, format="json")

        self.assertEqual(response.status_code, 400)

        self.wallet_from.refresh_from_db()
        self.wallet_to.refresh_from_db()

        self.assertEqual(self.wallet_from.balance, Decimal("1000.0000"))
        self.assertEqual(self.wallet_to.balance, Decimal("100.0000"))

    def test_transfer_different_currency(self):
        wallet_eur = Wallet.objects.create(
            user=self.other_user,
            currency="EUR",
            balance=Decimal("0.0000")
        )

        response = self.client.post(self.url, {
            "wallet_from_address": str(self.wallet_from.wallet_address),
            "wallet_to_address": str(wallet_eur.wallet_address),
            "amount": "100.0000",
            "idempotency_key": str(uuid.uuid4())
        }, format="json")

        self.assertEqual(response.status_code, 400)

    def test_transfer_idempotency(self):
        key = str(uuid.uuid4())

        payload = {
            "wallet_from_address": str(self.wallet_from.wallet_address),
            "wallet_to_address": str(self.wallet_to.wallet_address),
            "amount": "200.0000",
            "idempotency_key": key
        }

        r1 = self.client.post(self.url, payload, format="json")
        r2 = self.client.post(self.url, payload, format="json")

        self.assertEqual(r1.status_code, 201)
        self.assertEqual(r2.status_code, 201)

        self.wallet_from.refresh_from_db()
        self.wallet_to.refresh_from_db()

        self.assertEqual(self.wallet_from.balance, Decimal("800.0000"))
        self.assertEqual(self.wallet_to.balance, Decimal("300.0000"))
