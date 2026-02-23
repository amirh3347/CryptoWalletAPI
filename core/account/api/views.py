from django.contrib.auth import get_user_model

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from account.api.serializers import RegisterSerializer, LoginSerializer


class RegisterViewSet(CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = RegisterSerializer
    permission_classes = []


class LoginViewSet(CreateAPIView):
    queryset = get_user_model().objects.filter(is_active=True)
    serializer_class = LoginSerializer
    permission_classes = []


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token = RefreshToken.for_user(user)
        access_token = str(token.access_token)
        refresh_token = str(token)

        response = {"access_token": access_token, "refresh_token": refresh_token, "username": user.username}
        return Response(response)
