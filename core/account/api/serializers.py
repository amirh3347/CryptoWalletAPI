from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from rest_framework import serializers
from rest_framework.exceptions import NotFound


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, min_length=3, max_length=30)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True, required=True,
        style={
            'input_type': 'password',
        }
    )
    confirm_password = serializers.CharField(
        max_length=68, min_length=6, write_only=True, required=True,
        style={
            'input_type': 'password',
        }
    )

    class Meta:
        model = User
        fields = ["username", "password", "confirm_password"]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"details": "Passwords does not match"}
            )

        if User.objects.filter(username=attrs.get("username")).exists():
            raise serializers.ValidationError(
                {"detail": "Username already exists"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer, ModelBackend):
    username = serializers.CharField(required=True, min_length=3, max_length=30)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["username", 'password']


    def validate(self, attrs):
        attrs["user"] = None
        username = attrs.get('username')
        password = attrs.get('password')

        try:
            user = User.objects.get(is_active=True, username=username)

        except:
            raise NotFound("User not found")

        user = self.authenticate(request=self.context["request"], username=username, password=password)
        if not user:
            raise serializers.ValidationError("authentication failed please check your inputs")
        else:
            attrs["user"] = user
        return super().validate(attrs)
