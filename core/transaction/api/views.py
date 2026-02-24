import uuid

from django.db.models import Q

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from drf_spectacular.utils import extend_schema, OpenApiResponse

from transaction.api.serializers import DepositSerializer, WithdrawSerializer, TransferSerializer, TransactionLedgerSerializer
from transaction.services import deposit, withdraw, transfer
from transaction.models import TransactionLedger


class DepositView(generics.GenericAPIView):
    serializer_class = DepositSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Deposit funds into a wallet",
        request=DepositSerializer,
        responses={201: TransactionLedgerSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        wallet = serializer.wallet_instance
        amount = serializer.validated_data["amount"]
        ledger = deposit(wallet, amount, serializer.validated_data.get("idempotency_key"))
        return Response(TransactionLedgerSerializer(ledger).data, status=status.HTTP_201_CREATED)


class WithdrawView(generics.GenericAPIView):
    serializer_class = WithdrawSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Withdraw funds from a wallet",
        request=WithdrawSerializer,
        responses={201: TransactionLedgerSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        wallet = serializer.wallet_instance
        amount = serializer.validated_data["amount"]
        ledger = withdraw(wallet, amount, serializer.validated_data.get("idempotency_key"))
        return Response(TransactionLedgerSerializer(ledger).data, status=status.HTTP_201_CREATED)


class TransferView(generics.GenericAPIView):
    serializer_class = TransferSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Transfer funds between wallets",
        request=TransferSerializer,
        responses={201: TransactionLedgerSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        wallet_from = serializer.wallet_from_instance
        wallet_to = serializer.wallet_to_instance
        amount = serializer.validated_data["amount"]
        ledger = transfer(wallet_from, wallet_to, amount, serializer.validated_data.get("idempotency_key"))
        return Response(TransactionLedgerSerializer(ledger).data, status=status.HTTP_201_CREATED)


class LedgerListView(generics.ListAPIView):
    serializer_class = TransactionLedgerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user

        return (
            TransactionLedger.objects
            .filter(
                Q(wallet_from__user=user) |
                Q(wallet_to__user=user)
            )
            .select_related("wallet_from", "wallet_to")
            .order_by("-created_date")
        )

    @extend_schema(
        summary="List user transactions",
        description="""
            Returns all transactions initiated by the authenticated user (wallet_from).

            The response is paginated with `limit` and `offset` query parameters.
            Each record is immutable and contains the following fields:
            - id
            - wallet_from
            - wallet_to
            - amount
            - currency
            - transaction_type
            - status
            - created_date
            - idempotency_key
            """,
        responses=OpenApiResponse(
            response=TransactionLedgerSerializer,
            description="Paginated list of transactions for the authenticated user"
        ),
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GenerateIdempotencyKeyView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Generate unique idempotency key",
        description="Returns a new UUID that client can use as idempotency_key for transactions.",
        responses={200: {"type": "object", "properties": {"idempotency_key": {"type": "string"}}}},
    )
    def get(self, request):
        key = uuid.uuid4()
        return Response({"idempotency_key": str(key)})
