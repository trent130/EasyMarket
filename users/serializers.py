from rest_framework import serializers
import string
import pyotp
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import UserProfile, Student, CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    full_name = serializers.ReadOnlyField()
    user_type_display = serializers.ReadOnlyField(source='get_user_type_display_name')

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'email', 'password', 'user_type', 'user_type_display', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value



class StudentProfileSerializer(serializers.ModelSerializer):
    # User-related fields
    user_id = serializers.UUIDField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    user_type = serializers.CharField(source='user.user_type', read_only=True)
    
    # Profile fields
    avatar = serializers.ImageField(source='user.userprofile.avatar', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'user_id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'user_type', 'bio', 'phone_number', 'date_of_birth', 'university', 'student_id',
            'avatar', 'two_factor_enabled', 'two_factor_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'two_factor_verified']
    
    def update(self, instance, validated_data):
        # Handle user profile updates if needed
        return super().update(instance, validated_data)


class TwoFactorEnableSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()

    def validate(self, data):
        """
        Validate that the user exists and 2FA is not enabled. If both
        conditions are met, return the data. If not, raise a
        serializers.ValidationError with a suitable message.
        """
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
        """
        Validate that the token consists only of digits.

        Args:
            value (str): The token to be validated.

        Returns:
            str: The validated token if it contains only digits.

        Raises:
            serializers.ValidationError: If the token contains non-digit characters.
        """
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
        """
        Validate that the token consists only of digits.

        Args:
            value (str): The token to be validated.

        Returns:
            str: The validated token if it contains only digits.

        Raises:
            serializers.ValidationError: If the token contains non-digit characters.
        """
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
        """
        Validate that the code contains only uppercase letters and numbers.

        Args:
            value (str): The code to be validated.

        Returns:
            str: The validated code if it contains only valid characters.

        Raises:
            serializers.ValidationError: If the code contains invalid characters.
        """
        if not all(c in string.ascii_uppercase + string.digits for c in value):
            raise serializers.ValidationError(
                "Code must contain only uppercase letters and numbers"
            )
        return value


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate that the given username and password are valid.

        Args:
            data (dict): Dictionary containing the username and password.

        Returns:
            dict: The validated data if the username and password are valid.

        Raises:
            serializers.ValidationError: If the username and password are invalid.
        """
        user = CustomUser.objects.filter(username=data['username']).first()
        if user is None or not user.check_password(data['password']):
            raise serializers.ValidationError("Invalid credentials")
        return data


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm', 'user_type']
        extra_kwargs = {
            'user_type': {'default': 'student'}
        }

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'avatar', 'user_info']
        extra_kwargs = {
            'user': {'read_only': True}
        }
    
    def get_user_info(self, obj):
        """Return user information"""
        return {
            'username': obj.user.username,
            'email': obj.user.email,
            'full_name': obj.user.full_name,
            'user_type': obj.user.user_type
        }
    
    def update(self, instance, validated_data):
        # Handle avatar updates
        return super().update(instance, validated_data)


class AuthResponseSerializer(serializers.Serializer):
    """Serializer for authentication response"""
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user = CustomUserSerializer(read_only=True)
    student_profile = StudentProfileSerializer(read_only=True, required=False)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Validate that the given email address exists in the database.

        Args:
            value (str): The email address to be validated.

        Returns:
            str: The validated email address if it exists.

        Raises:
            serializers.ValidationError: If the email address does not exist.
        """
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


