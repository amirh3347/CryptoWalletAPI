from django.contrib.auth import get_user_model

from rest_framework.generics import CreateAPIView

from account.api.serializers import RegisterSerializer


class RegisterViewSet(CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = RegisterSerializer
    permission_classes = []
