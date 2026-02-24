import uuid

from decimal import Decimal

from django.db import models

from wallet.models import Wallet, CurrencyChoices


class TransactionType(models.TextChoices):
    DEPOSIT = "DEPOSIT", "Deposit"
    WITHDRAW = "WITHDRAW", "Withdraw"
    TRANSFER = "TRANSFER", "Transfer"


class TransactionLedger(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet_from = models.ForeignKey(
        Wallet, null=True, blank=True, on_delete=models.PROTECT, related_name="transactions_from"
    )
    wallet_to = models.ForeignKey(
        Wallet, null=True, blank=True, on_delete=models.PROTECT, related_name="transactions_to"
    )
    amount = models.DecimalField(max_digits=18, decimal_places=4)
    currency = models.CharField(max_length=10, choices=CurrencyChoices.choices)
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    status = models.CharField(max_length=20, default="COMPLETED")
    created_date = models.DateTimeField(auto_now_add=True)
    idempotency_key = models.UUIDField(max_length=64, unique=True, null=True, blank=True)

    class Meta:
        ordering = ["-created_date"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gt=Decimal("0.0000")),
                name="transaction_amount_positive"
            ),
        ]
        indexes = [
            models.Index(fields=["wallet_from"]),
            models.Index(fields=["wallet_to"]),
            models.Index(fields=["currency"]),
            models.Index(fields=["idempotency_key"]),
        ]

    def __str__(self):
        return f"{self.transaction_type} {self.amount} {self.currency}"
