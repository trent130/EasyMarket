from django.shortcuts import render
import secrets
import string
import json
import time
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, logout
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Student, CustomUser, UserProfile
from .serializers import (
    # TwoFactorEnableSerializer,
    TwoFactorVerifySerializer,
    TwoFactorStatusSerializer,
    # TwoFactorDisableSerializer,
    BackupCodesSerializer,
    ValidateBackupCodeSerializer
)
from django.conf import settings 
import redis
import logging
import pyotp
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone  # Import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.parsers import JSONParser

logger = logging.getLogger(__name__)
RATE_LIMIT_STORE = []
RATE_LIMIT_WINDOW = 60 * 60
RATE_LIMIT_MAX_REQUESTS = 5
RATE_LIMIT_PREFIX = "password_reset_rate_limit:"
REDIS_HOST = settings.REDIS_HOST if hasattr(settings, "REDIS_HOST") else 'localhost'
REDIS_PORT = settings.REDIS_PORT if hasattr(settings, "REDIS_PORT") else '6379'
REDIS_DB = settings.REDIS_DB if hasattr(settings, "REDIS_DB") else 0
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT, 
    db=REDIS_DB,
   # decode_string=True
)
from .serializers import UserProfileSerializer


# Create your views here.
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:  # Prevent duplicate profiles for superusers
        UserProfile.objects.get_or_create(user=instance)  # Ensures no duplicate profiles


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user profiles.
    Supports retrieving and updating user profile information.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access this
    parser_classes = (MultiPartParser, FormParser)  # Allow file uploads

    def get_queryset(self):
        """
        Restricts the returned profiles to the logged-in user.
        """
        return UserProfile.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        """
        Ensures that the user can only update their own profile.
        """
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve the authenticated user's profile.
        """
        instance = self.get_queryset().first()  # Get the current user's profile
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
    """Enable 2FA for a user"""
    user = get_object_or_404(CustomUser, id=request.data.get('user_id'))

    if user.isTwoFactorEnabled:
        return Response({'error': 'Two-factor authentication is already enabled'}, status=status.HTTP_400_BAD_REQUEST)

    secret = pyotp.random_base32()
    user.twoFactorSecret = secret
    user.save()

    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(user.email, issuer_name="EasyMarket")

    return Response({'secret': secret, 'qr_code_url': provisioning_uri})


@api_view(['POST'])
@permission_classes([AllowAny])
def signin(request):
    """Sign in a user"""
    username_or_email = request.data.get('username') or request.data.get('email')
    password = request.data.get('password')
    print(password)
    print(username_or_email)

    if not username_or_email or not password:
        return Response({'error': 'Please provide both username/email and password'}, status=status.HTTP_400_BAD_REQUEST)

    if '@' in username_or_email:
        try:
            print("email called")
            user = CustomUser.objects.get(email=username_or_email)
            username = user.username
        except CustomUser.DoesNotExist:
            print("email not called")
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        print("username called")
        username = username_or_email
    user = authenticate(request, username=username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({'refresh': str(refresh), 'access': str(refresh.access_token), 'user_id': user.id, 'email': user.email}, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
# @parser_classes([JSONParser])
def signup(request):
    """Sign up a user"""
    print("Register view called")

    try:
        data = request.data
        if isinstance(data, str):
            data = json.loads(data)  # convert from string to dict if necessary
    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)

    print("Request data:", request.data)

    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response({'error': 'Please provide username, email, and password'}, status=status.HTTP_400_BAD_REQUEST)

    if CustomUser.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    if CustomUser.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = CustomUser.objects.create_user(username=username, email=email, password=password)
    # Check if a Student object already exists for this user
    if not Student.objects.filter(user=user).exists():
        Student.objects.create(user=user) #This line should not exist if there is a student

    return Response({'message': 'CustomUser created successfully. Redirecting to login...'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa(request):
    """Verify 2FA token"""
    student = get_object_or_404(Student, user=request.user)
    if not student.two_factor_enabled:
        return Response({'error': '2FA is not enabled'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = TwoFactorVerifySerializer(data=request.data)
    if serializer.is_valid():
        if student.two_factor_secret != serializer.validated_data['secret']:
            return Response({'error': 'Invalid secret'}, status=status.HTTP_400_BAD_REQUEST)

        student.two_factor_verified = True
        student.save()

        return Response({'success': True})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_2fa_status(request):
    """Get 2FA status for a user"""
    student = get_object_or_404(Student, user=request.user)
    serializer = TwoFactorStatusSerializer(student)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    """Disable 2FA for a user"""
    user = get_object_or_404(CustomUser, id=request.user.id)

    if not user.isTwoFactorEnabled:
        return Response({'error': 'Two-factor authentication is not enabled'}, status=status.HTTP_400_BAD_REQUEST)

    user.isTwoFactorEnabled = False
    user.twoFactorSecret = None
    user.save()

    return Response({'message': 'Two-factor authentication has been disabled'})


def rate_limit(email):
    '''
    applying redis based rate limiting for requests:
        False for not allowed and True for allowed
    '''
    key = f"{RATE_LIMIT_PREFIX}{email}"
    now = int(time.time())

    pipe = redis_client.pipeline()
    pipe.zremrangebyscore(key, 0, now - RATE_LIMIT_WINDOW)
    pipe.zcard(key)

    pipe.zadd(key, {now: now})
    pipe.expire(key, RATE_LIMIT_WINDOW)

    count, _, _ = pipe.execute()

    if count >= RATE_LIMIT_MAX_REQUESTS:
        return False
    return True


async def send_password_reset_email(email, reset_token):
    subject = "Password Reset Request"
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    html_message = render_to_string('emails/password_reset_email.html', {
        'reset_link': reset_link,
        'email': email
    })
    plain_message = render_to_string( 'emails/password_reset_email.html', {
    'reset_link': reset_link,
    'email': email
    })

    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message = html_message,
            fail_silently = False
        )
        print(f"Password reset email sent to {email}")
    except Exception as e:
        print(f"Error sending password reset email {email}: {e}")


@api_view(['POST'])
@permission_classes([AllowAny])
async def forgot_password(request):
    """Handle forgot password"""
    email = request.data.get('email')

    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    if not rate_limit(email):
        return Response({'error': 'Too many requests. Please try again later.'},
                        status=status.HTTP_429_TOO_MANY_REQUESTS)
    alphabet = string.ascii_letters + string.digits + string.puntuation
    reset_token = "".join(secrets.choice(alphabet))
    reset_token_expiry = timezone.now() + timezone.timedelta(hours=0.5)

    user = get_object_or_404(CustomUser, email=email)
    user.resetToken = reset_token
    user.resetTokenExpiry = reset_token_expiry
    user.save()

    await send_password_reset_email(email, reset_token)

    return Response({'message': 'If an account exists for this email, a password reset link has been sent.'})


@api_view(['PUT'])
@permission_classes([AllowAny])
async def reset_password(request):
    """Reset password using the reset token"""
    token = request.data.get('token')
    new_password = request.data.get('newPassword')

    if not token or not new_password:
        return Response({'error': 'Token and new password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(CustomUser, resetToken=token, resetTokenExpiry__gt=timezone.now())

    hashed_password = await hash(new_password, 10)
    user.password = hashed_password
    user.resetToken = None
    user.resetTokenExpiry = None
    user.save()

    return Response({'message': 'Password has been reset successfully'})

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
async def change_password(request):
    """Change password using the change password token"""
    # TODO: implement a functionality to change password

    return Response({'message': 'Password has been changed successfully'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_backup_code(request):
    """Validate a backup code for 2FA recovery"""
    student = get_object_or_404(Student, user=request.user)
    if not student.two_factor_enabled:
        return Response({'error': '2FA is not enabled'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = ValidateBackupCodeSerializer(data=request.data)
    if serializer.is_valid():
        if student.verify_backup_code(serializer.validated_data['code']):
            return Response({'success': True})
        return Response({'error': 'Invalid backup code'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signout(request):
    """Logout a user"""
    user = request.user
    logout(request, user)
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def regenerate_backup_codes(request):
#     """Regenerate backup codes for 2FA"""
#     student = get_object_or_404(Student, user=request.user)
#     if not student.two_factor_enabled:
#         return Response({'error': '2FA is not enabled'}, status=status.HTTP_400_BAD_REQUEST)

#     backup_codes = student.generate_backup_codes()
#     serializer = BackupCodesSerializer(data={'codes': backup_codes})
#     if serializer.is_valid():
#         return Response(serializer.data)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     def validate(self, attrs):
#         try:
#             data = super().validate(attrs)
#             data['user_id'] = self.user.id
#             data['email'] = self.user.email
#             return data
#         except Exception as e:
#             logger.error(f"Token generation error: {str(e)}")
#             raise


# class CustomTokenObtainPairView(TokenObtainPairView):
#     serializer_class = CustomTokenObtainPairSerializer

#     def post(self, request, *args, **kwargs):
#         try:
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             return Response(serializer.validated_data)
#         except Exception as e:
#             logger.error(f"Unexpected token generation error: {str(e)}")
#             return Response({'error': 'Authentication failed', 'details': str(e)},
# status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# #         return Response({'success': True})
# #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_backup_codes(request):
    """Regenerate backup codes for 2FA"""
    student = get_object_or_404(Student, user=request.user)
    if not student.two_factor_enabled:
        return Response(
            {'error': '2FA is not enabled'},
            status=status.HTTP_400_BAD_REQUEST
        )

    backup_codes = student.generate_backup_codes()
    serializer = BackupCodesSerializer(data={'codes': backup_codes})
    if serializer.is_valid():
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            # Add additional user information
            data['user_id'] = self.user.id
            data['email'] = self.user.email
            return data
        except Exception as e:
            # Detailed error logging
            logger.error(f"Token generation error: {str(e)}")
            raise


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            # Validate and handle errors explicitly
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                # Log validation errors
                logger.error(f"Token validation error: {str(e)}")
                return Response({
                    'error': 'Invalid credentials',
                    'details': str(e)
                }, status=status.HTTP_401_UNAUTHORIZED)

            return Response(serializer.validated_data)
        except Exception as e:
            logger.error(f"Unexpected token generation error: {str(e)}")
            return Response({
                'error': 'Authentication failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# TODO: 1: implement the change password functionality, look at the user types and start aggregating them per 
# account type and permissions also
# TODO: 2: issues with the signup functionality, something to do with 'str' does not have a 'get' method.