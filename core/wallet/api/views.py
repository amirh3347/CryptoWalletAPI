from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from wallet.models import Wallet
from wallet.api.serializers import WalletCreateSerializer, WalletListSerializer


class WalletListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return WalletCreateSerializer
        return WalletListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="List User Wallets",
        description="Return all wallets that belong to the authenticated user.",
        responses={200: WalletListSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create Wallet",
        description="""
            Create a new wallet for the authenticated user.
            
            Each user can have only one wallet per currency.
            If a wallet with the same currency already exists,
            API will return 400.
            """,
        request=WalletCreateSerializer,
        responses={
            201: WalletListSerializer,
            400: None,
            401: None,
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        output_serializer = WalletListSerializer(serializer.instance, context={"request": request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
