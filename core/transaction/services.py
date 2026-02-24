import uuid

from decimal import Decimal

from django.db import transaction

from rest_framework.exceptions import ValidationError

from wallet.models import Wallet
from transaction.models import TransactionLedger, TransactionType


def deposit(wallet: Wallet, amount: Decimal, idempotency_key: uuid.UUID) -> TransactionLedger:
    if amount <= 0:
        raise ValidationError("Amount must be positive")

    existing = TransactionLedger.objects.filter(idempotency_key=idempotency_key).first()
    if existing:
        return existing

    before_balance = wallet.balance

    with transaction.atomic():
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
        wallet.balance += amount
        wallet.save()

        if not (before_balance + amount == wallet.balance):
            raise ValidationError("error in transaction")

        ledger = TransactionLedger.objects.create(
            wallet_to=wallet,
            amount=amount,
            currency=wallet.currency,
            transaction_type=TransactionType.DEPOSIT,
            idempotency_key=idempotency_key,
        )
        return ledger


def withdraw(wallet: Wallet, amount: Decimal, idempotency_key: uuid.UUID) -> TransactionLedger:
    if amount <= 0:
        raise ValidationError("Amount must be positive")

    existing = TransactionLedger.objects.filter(idempotency_key=idempotency_key).first()
    if existing:
        return existing

    before_balance = wallet.balance

    with transaction.atomic():
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)
        if wallet.balance < amount:
            raise ValidationError("Insufficient balance")
        wallet.balance -= amount
        wallet.save()

        if not (before_balance - amount == wallet.balance):
            raise ValidationError("error in transaction")

        ledger = TransactionLedger.objects.create(
            wallet_from=wallet,
            amount=amount,
            currency=wallet.currency,
            transaction_type=TransactionType.WITHDRAW,
            idempotency_key=idempotency_key,
        )
        return ledger


def transfer(wallet_from: Wallet, wallet_to: Wallet, amount: Decimal, idempotency_key: uuid.UUID) -> TransactionLedger:
    if amount <= 0:
        raise ValidationError("Amount must be positive")
    if wallet_from.currency != wallet_to.currency:
        raise ValidationError("Wallet currencies must match")

    existing = TransactionLedger.objects.filter(idempotency_key=idempotency_key).first()
    if existing:
        return existing

    sender_before_balance = wallet_from.balance
    receiver_before_balance = wallet_to.balance

    with transaction.atomic():
        wallet_from = Wallet.objects.select_for_update().get(pk=wallet_from.pk)
        wallet_to = Wallet.objects.select_for_update().get(pk=wallet_to.pk)

        if wallet_from.balance < amount:
            raise ValidationError("Insufficient balance")

        wallet_from.balance -= amount
        wallet_to.balance += amount
        wallet_from.save()
        wallet_to.save()

        if not (sender_before_balance - amount == wallet_from.balance) or not \
            (receiver_before_balance + amount == wallet_to.balance):
            raise ValidationError("error in transaction")

        ledger = TransactionLedger.objects.create(
            wallet_from=wallet_from,
            wallet_to=wallet_to,
            amount=amount,
            currency=wallet_from.currency,
            transaction_type=TransactionType.TRANSFER,
            idempotency_key=idempotency_key,
        )
        return ledger
