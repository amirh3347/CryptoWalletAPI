from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from account.api.views import RegisterViewSet, LoginViewSet



urlpatterns = [

    path('v1/register/', RegisterViewSet.as_view(), name='register'),
    path('v1/login/', LoginViewSet.as_view(), name='login'),
    path('v1/refresh/', TokenRefreshView.as_view(), name='refresh'),
]
