from django.urls import path

from account.api.views import RegisterViewSet, LoginViewSet, CustomTokenRefreshView


app_name = "account"

urlpatterns = [

    path('v1/register/', RegisterViewSet.as_view(), name='register'),
    path('v1/login/', LoginViewSet.as_view(), name='login'),
    path('v1/refresh/', CustomTokenRefreshView.as_view(), name='refresh'),
]
