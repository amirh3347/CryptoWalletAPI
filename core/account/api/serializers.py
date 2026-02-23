from django.contrib.auth import get_user_model

from rest_framework import serializers


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