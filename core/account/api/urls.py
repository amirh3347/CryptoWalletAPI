from django.urls import path

from account.api.views import RegisterViewSet, LoginViewSet



urlpatterns = [

    path('v1/register/', RegisterViewSet.as_view(), name='register'),
    path('v1/login/', LoginViewSet.as_view(), name='login'),
]
