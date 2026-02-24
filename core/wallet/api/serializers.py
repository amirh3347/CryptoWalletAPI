from decimal import Decimal

from rest_framework import serializers

from wallet.models import Wallet


class WalletCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = ["currency"]

    def validate_currency(self, value):
        user = self.context["request"].user
        if Wallet.objects.filter(user=user, currency=value).exists():
            raise serializers.ValidationError("You already have a wallet with this currency.")
        return value


class WalletListSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=18, decimal_places=4, read_only=True, min_value=Decimal("0.0000"),
                                       default=Decimal("0.0000"))

    class Meta:
        model = Wallet
        fields = [
            "wallet_address",
            "currency",
            "balance",
            "created_date",
        ]
