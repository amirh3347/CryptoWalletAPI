from django.urls import path

from wallet.api.views import WalletListCreateView


app_name = "wallet"

urlpatterns = [
    path("v1/", WalletListCreateView.as_view(), name="wallet-list-create"),
]
