import threading
import uuid
import time

from decimal import Decimal

from django.test import TransactionTestCase
from django.contrib.auth import get_user_model

from wallet.models import Wallet
from transaction.services import withdraw


User = get_user_model()


class IsolationLevelTest(TransactionTestCase):

    reset_sequences = True

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

    def test_select_for_update_blocks(self):

        results = []

        def first():
            withdraw(self.wallet, Decimal("900.0000"), uuid.uuid4())
            time.sleep(2)
            results.append("first_done")

        def second():
            try:
                withdraw(self.wallet, Decimal("900.0000"), uuid.uuid4())
            except Exception:
                results.append("second_failed")

        t1 = threading.Thread(target=first)
        t2 = threading.Thread(target=second)

        t1.start()
        time.sleep(0.5)
        t2.start()

        t1.join()
        t2.join()

        self.wallet.refresh_from_db()

        self.assertEqual(self.wallet.balance, Decimal("100.0000"))
        self.assertIn("second_failed", results)
