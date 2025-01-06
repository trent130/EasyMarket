import string
from rest_framework import serializers
from .models import Student, User
import pyotp


class TwoFactorEnableSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate(self, data):
        try:
            student = Student.objects.get(user_id=data['user_id'])
            if student.two_factor_enabled:
                raise serializers.ValidationError("2FA is already enabled")
            return data
        except Student.DoesNotExist:
            raise serializers.ValidationError("Student not found")


class TwoFactorVerifySerializer(serializers.Serializer):
    token = serializers.CharField(max_length=6, min_length=6)
    secret = serializers.CharField()

    def validate_token(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Token must contain only digits")
        return value

    def validate(self, data):
        totp = pyotp.TOTP(data['secret'])
        if not totp.verify(data['token']):
            raise serializers.ValidationError("Invalid token")
        return data


class TwoFactorStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['two_factor_enabled', 'two_factor_verified']


class TwoFactorDisableSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=6, min_length=6)
    
    def validate_token(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Token must contain only digits")
        return value


class BackupCodesSerializer(serializers.Serializer):
    codes = serializers.ListField(
        child=serializers.CharField(max_length=8, min_length=8)
    )


class ValidateBackupCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=8, min_length=8)

    def validate_code(self, value):
        if not all(c in string.ascii_uppercase + string.digits for c in value):
            raise serializers.ValidationError(
                "Code must contain only uppercase letters and numbers"
            )
        return value


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = User.objects.filter(username=data['username']).first()
        if user is None or not user.check_password(data['password']):
            raise serializers.ValidationError("Invalid credentials")
        return data


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value