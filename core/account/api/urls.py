from django.urls import path

from account.api.views import RegisterViewSet



urlpatterns = [

    path('v1/register/', RegisterViewSet.as_view(), name='register'),
]
