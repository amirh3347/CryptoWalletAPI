from django.urls import path
from transaction.api.views import DepositView, WithdrawView, TransferView, LedgerListView, GenerateIdempotencyKeyView

app_name = "transactions"

urlpatterns = [
    path("v1/deposit/", DepositView.as_view(), name="deposit"),
    path("v1/withdraw/", WithdrawView.as_view(), name="withdraw"),
    path("v1/transfer/", TransferView.as_view(), name="transfer"),
    path("v1/ledger/", LedgerListView.as_view(), name="ledger-list"),
    path("v1/idempotency-key/", GenerateIdempotencyKeyView.as_view(), name="idempotency-key"),
]
