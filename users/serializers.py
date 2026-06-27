from rest_framework import serializers
import string
import pyotp
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import UserProfile, Student, UserPreferences
from django.contrib.auth import authenticate
CustomUser = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    full_name = serializers.ReadOnlyField()
    user_type_display = serializers.ReadOnlyField(source='get_user_type_display_name')

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'email', 'password', 'user_type', 'user_type_display', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']

    def create(self, validated_data):  # pragma: no cover
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate_password(self, value):  # pragma: no cover
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

    def validate(self, data):  # pragma: no cover
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

    def validate_token(self, value):  # pragma: no cover
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
    username_or_email = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate that the given username/email and password are valid.
        """
        username_or_email = data['username_or_email']
        password = data['password']

        # Use authenticate() which will utilize our custom backend
        user = authenticate(
            request=self.context.get('request'),
            username=username_or_email,
            password=password
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        data['user'] = user
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

    def validate_password(self, value):  # pragma: no cover
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate_username(self, value):  # pragma: no cover
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):  # pragma: no cover
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

    def validate_email(self, value):  # pragma: no cover
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

class ChangePasswordSerializer(serializers.Serializer):
    def validate_user(self, value):  # pragma: no cover
        pass


class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = ['email_notifications', 'push_notifications', 'dark_mode', 'language', 'currency', 'timezone']


class CurrentUserSerializer(serializers.ModelSerializer):
    """Flattened serializer: user fields + student fields merged into one object."""
    full_name = serializers.ReadOnlyField()
    user_type_display = serializers.ReadOnlyField(source='get_user_type_display_name')
    avatar = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    university = serializers.SerializerMethodField()
    student_id = serializers.SerializerMethodField()
    two_factor_enabled = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'first_name', 'last_name', 'full_name', 'email',
            'user_type', 'user_type_display', 'is_active', 'date_joined',
            'email_verified', 'avatar',
            'bio', 'phone_number', 'university', 'student_id', 'two_factor_enabled',
        ]
        read_only_fields = fields

    def get_avatar(self, obj):
        try:
            request = self.context.get('request')
            avatar = obj.userprofile.avatar
            if avatar and request:
                return request.build_absolute_uri(avatar.url)
        except Exception:
            pass
        return None

    def _get_student(self, obj):
        try:
            return obj.student_profile
        except Student.DoesNotExist:
            return None

    def get_bio(self, obj):
        s = self._get_student(obj)
        return s.bio if s else ''

    def get_phone_number(self, obj):
        s = self._get_student(obj)
        return s.phone_number if s else ''

    def get_university(self, obj):
        s = self._get_student(obj)
        return s.university if s else ''

    def get_student_id(self, obj):
        s = self._get_student(obj)
        return s.student_id if s else None

    def get_two_factor_enabled(self, obj):
        s = self._get_student(obj)
        return s.two_factor_enabled if s else False
