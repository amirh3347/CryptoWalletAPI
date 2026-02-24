import uuid

from decimal import Decimal

from concurrent.futures import ThreadPoolExecutor

from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from django.db import connections

from wallet.models import Wallet
from transaction.services import deposit, withdraw, transfer


User = get_user_model()


class TransactionServiceTest(TransactionTestCase):

    reset_sequences = True

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="amir",
            password="123456"
        )

        self.user2 = User.objects.create_user(
            username="ali",
            password="123456"
        )

        self.wallet = Wallet.objects.create(
            user=self.user1,
            currency="USD",
            balance=Decimal("1000.0000")
        )

        self.second_wallet = Wallet.objects.create(
            user=self.user2,
            currency="USD",
            balance=Decimal("0.0000")
        )

    def test_ledger_update_forbidden(self):
        key = uuid.uuid4()
        ledger = deposit(self.wallet, Decimal("50.0000"), key)

        ledger.amount = Decimal("999.0000")

        with self.assertRaises(Exception):
            ledger.save()

    def test_ledger_delete_forbidden(self):
        key = uuid.uuid4()
        ledger = deposit(self.wallet, Decimal("50.0000"), key)

        with self.assertRaises(Exception):
            ledger.delete()

    def test_concurrent_withdraw(self):

        key1 = uuid.uuid4()
        key2 = uuid.uuid4()

        def withdraw_call(key):
            try:
                withdraw(self.wallet, Decimal("800.0000"), key)
                return "success"
            except Exception:
                return "failed"
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(withdraw_call, [key1, key2]))

        self.wallet.refresh_from_db()

        self.assertEqual(results.count("success"), 1)
        self.assertEqual(results.count("failed"), 1)
        self.assertEqual(self.wallet.balance, Decimal("200.0000"))

    def test_concurrent_transfer(self):
        key1 = uuid.uuid4()
        key2 = uuid.uuid4()

        def transfer_call(key):
            try:
                transfer(
                    self.wallet,
                    self.second_wallet,
                    Decimal("900.0000"),
                    key
                )
                return "success"
            except Exception:
                return "failed"
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(transfer_call, [key1, key2]))

        self.wallet.refresh_from_db()
        self.second_wallet.refresh_from_db()

        self.assertEqual(results.count("success"), 1)
        self.assertEqual(results.count("failed"), 1)
        self.assertEqual(self.wallet.balance, Decimal("100.0000"))
