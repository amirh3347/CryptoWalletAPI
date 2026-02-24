from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from drf_spectacular.utils import extend_schema

from account.api.serializers import RegisterSerializer, LoginSerializer, LoginResponseSerializer, \
                                    RefreshDebugResponseSerializer, RefreshProdResponseSerializer


class RegisterViewSet(CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = RegisterSerializer
    permission_classes = []

    @extend_schema(
        summary="User Registration",
        description="Create a new user account with username and password.",
        request=RegisterSerializer,
        responses={
            201: RegisterSerializer,
            400: None,
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LoginViewSet(CreateAPIView):
    queryset = get_user_model().objects.filter(is_active=True)
    serializer_class = LoginSerializer
    permission_classes = []

    @extend_schema(
        summary="User Login",
        description="Authenticate user and return JWT access and refresh tokens.",
        request=LoginSerializer,
        responses={
            200: LoginResponseSerializer,
            400: None,
            404: None,
        }
    )
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


class CustomTokenRefreshView(TokenRefreshView):

    @extend_schema(
        summary="Refresh Access Token",
        description="""
            Generate a new access token using a valid refresh token.
            
            Behavior depends on environment:
            
            - In DEBUG mode:
              Returns only a new `access` token.
            
            - In Production:
              Returns both a new `access` token and a rotated `refresh` token.
            """,
        request=TokenRefreshSerializer,
        responses={
            200: (RefreshProdResponseSerializer if not settings.DEBUG else RefreshDebugResponseSerializer),
            401: None,
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
