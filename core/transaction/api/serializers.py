from decimal import Decimal

from rest_framework import serializers

from drf_spectacular.utils import extend_schema_field, OpenApiTypes

from transaction.models import TransactionLedger
from wallet.models import Wallet


class TransactionLedgerSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(
        max_digits=18,
        decimal_places=4,
        read_only=True,
        min_value=Decimal("0.0000"),
        default=Decimal("100.0000"),
    )
    wallet_from = serializers.SerializerMethodField()
    wallet_to = serializers.SerializerMethodField()

    class Meta:
        model = TransactionLedger
        fields = [
            "id",
            "wallet_from",
            "wallet_to",
            "amount",
            "currency",
            "transaction_type",
            "status",
            "created_date",
            "idempotency_key",
        ]
        read_only_fields = fields

    @extend_schema_field(OpenApiTypes.UUID)
    def get_wallet_from(self, obj):
        if obj.wallet_from:
            return str(obj.wallet_from.wallet_address)
        return None

    @extend_schema_field(OpenApiTypes.UUID)
    def get_wallet_to(self, obj):
        if obj.wallet_to:
            return str(obj.wallet_to.wallet_address)
        return None


class DepositSerializer(serializers.Serializer):
    wallet_address = serializers.UUIDField(required=True)
    amount = serializers.DecimalField(max_digits=18, decimal_places=4, min_value=Decimal("0.0001"), default=Decimal("0.0001"))
    idempotency_key = serializers.UUIDField(required=True)

    wallet_instance: Wallet = None

    def validate_wallet_address(self, value):
        user = self.context["request"].user
        try:
            self.wallet_instance = Wallet.objects.get(wallet_address=value, user=user)
        except Wallet.DoesNotExist:
            raise serializers.ValidationError("Invalid wallet address")
        return value


class WithdrawSerializer(serializers.Serializer):
    wallet_address = serializers.UUIDField(required=True)
    amount = serializers.DecimalField(max_digits=18, decimal_places=4, min_value=Decimal("0.0001"), default=Decimal("0.0001"))
    idempotency_key = serializers.UUIDField(required=True)

    wallet_instance: Wallet = None

    def validate_wallet_address(self, value):
        user = self.context["request"].user
        try:
            self.wallet_instance = Wallet.objects.get(wallet_address=value, user=user)
        except Wallet.DoesNotExist:
            raise serializers.ValidationError("Invalid wallet address")
        return value


class TransferSerializer(serializers.Serializer):
    wallet_from_address = serializers.UUIDField(required=True)
    wallet_to_address = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=4, min_value=Decimal("0.0001"), default=Decimal("0.0001"))
    idempotency_key = serializers.UUIDField(required=True)

    wallet_from_instance: Wallet = None
    wallet_to_instance: Wallet = None

    def validate_wallet_from_address(self, value):
        user = self.context["request"].user
        try:
            self.wallet_from_instance = Wallet.objects.get(wallet_address=value, user=user)
        except Wallet.DoesNotExist:
            raise serializers.ValidationError("Invalid source wallet address")
        return value

    def validate_wallet_to_address(self, value):
        try:
            self.wallet_to_instance = Wallet.objects.get(wallet_address=value)
        except Wallet.DoesNotExist:
            raise serializers.ValidationError("Destination wallet does not exist.")
        return value
