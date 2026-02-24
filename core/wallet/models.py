import uuid

from django.conf import settings
from django.db import models


class CurrencyChoices(models.TextChoices):
    USD = "USD", "US Dollar"
    EUR = "EUR", "Euro"
    IRR = "IRR", "Iranian Rial"


class Wallet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="wallets")
    currency = models.CharField(max_length=10, choices=CurrencyChoices.choices)
    balance = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    wallet_address = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "currency")
        ordering = ["-created_date"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(balance__gte=0),
                name="wallet_balance_non_negative"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.currency}"
