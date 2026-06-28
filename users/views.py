from django.shortcuts import render
import secrets
import string
import json
import time
import json
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework import status, viewsets, permissions
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, logout
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Student, CustomUser, UserProfile, UserPreferences
from .serializers import (
    CustomUserSerializer,
    CurrentUserSerializer,
    UserPreferencesSerializer,
    TwoFactorEnableSerializer,
    TwoFactorVerifySerializer,
    TwoFactorStatusSerializer,
    TwoFactorDisableSerializer,
    BackupCodesSerializer,
    ValidateBackupCodeSerializer,
    SignInSerializer,
    SignUpSerializer,
    StudentProfileSerializer,
    UserProfileSerializer
)
from django.contrib.auth import authenticate
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
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.hashers import make_password
from asgiref.sync import sync_to_async

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
    student = get_object_or_404(Student, user=request.user)

    if student.two_factor_enabled:
        return Response({'error': 'Two-factor authentication is already enabled'}, status=status.HTTP_400_BAD_REQUEST)

    secret = pyotp.random_base32()
    student.two_factor_secret = secret
    student.two_factor_enabled = True
    student.save()

    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(student.email, issuer_name="EasyMarket")

    return Response({'secret': secret, 'qr_code_url': provisioning_uri})


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([JSONParser])  # Add JSONParser to handle JSON data properly
def signin(request):
    """Handle user signin with enhanced error logging and proper response formatting"""
    try:
        # Ensure request.data is a dict
        data = request.data
        if isinstance(data, str):
            data = json.loads(data)
            
        logger.debug(f"Signin attempt with data: {data}")
        serializer = SignInSerializer(data=data, context={'request': request})
        
        if not serializer.is_valid():
            logger.warning(f"SignIn validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        logger.info(f"User {user.username} signed in successfully")
        
        refresh = RefreshToken.for_user(user)
        response_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': str(user.id),  # Convert UUID to string
            'email': user.email,
            'username': user.username
        }
        
        logger.debug(f"Sending successful signin response for user {user.username}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON data: {str(e)}")
        return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Unexpected error in signin: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """Sign up a user with improved validation and response"""
    serializer = SignUpSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = serializer.save()
        
        # Prepare response data
        response_data = {
            'message': 'User created successfully',
            'user': CustomUserSerializer(user).data
        }
        
        # Add student profile if user is a student
        try:
            student_profile = Student.objects.get(user=user)
            response_data['student_profile'] = StudentProfileSerializer(student_profile).data
        except Student.DoesNotExist:
            pass
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return Response({'error': 'Failed to create user'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Get current user — flat object with user + student fields merged."""
    serializer = CurrentUserSerializer(request.user, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def user_settings(request):
    """Get or update user notification preferences and avatar."""
    prefs, _ = UserPreferences.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        try:
            profile = request.user.userprofile
            avatar_url = request.build_absolute_uri(profile.avatar.url) if profile.avatar else None
        except UserProfile.DoesNotExist:
            avatar_url = None

        return Response({
            'username': request.user.username,
            'email': request.user.email,
            'email_notifications': prefs.email_notifications,
            'push_notifications': prefs.push_notifications,
            'dark_mode': prefs.dark_mode,
            'language': prefs.language,
            'currency': prefs.currency,
            'timezone': prefs.timezone,
            'avatar': avatar_url,
        })

    # PATCH
    if 'avatar' in request.FILES:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.avatar = request.FILES['avatar']
        profile.save()

    bool_fields = {'email_notifications', 'push_notifications', 'dark_mode'}
    for field in ['email_notifications', 'push_notifications', 'dark_mode', 'language', 'currency', 'timezone']:
        if field in request.data:
            val = request.data[field]
            if field in bool_fields and isinstance(val, str):
                val = val.lower() in ('true', '1', 'yes')
            setattr(prefs, field, val)
    prefs.save()

    try:
        profile = request.user.userprofile
        avatar_url = request.build_absolute_uri(profile.avatar.url) if profile.avatar else None
    except UserProfile.DoesNotExist:
        avatar_url = None

    return Response({
        'username': request.user.username,
        'email': request.user.email,
        'email_notifications': prefs.email_notifications,
        'push_notifications': prefs.push_notifications,
        'dark_mode': prefs.dark_mode,
        'language': prefs.language,
        'currency': prefs.currency,
        'timezone': prefs.timezone,
        'avatar': avatar_url,
    })


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_student_profile(request):
    """Update student profile information"""
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = StudentProfileSerializer(student, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    student = get_object_or_404(Student, user=request.user)

    if not student.two_factor_enabled:
        return Response({'error': 'Two-factor authentication is not enabled'}, status=status.HTTP_400_BAD_REQUEST)

    student.two_factor_enabled = False
    student.two_factor_verified = False
    student.two_factor_secret = None
    student.backup_codes = []
    student.save()

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

    _, count, _, _ = pipe.execute()

    if count >= RATE_LIMIT_MAX_REQUESTS:
        return False
    return True


def send_password_reset_email(email, reset_token):
    subject = "Password Reset Request"
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    reset_link = f"{frontend_url}/reset-password?token={reset_token}"

    try:
        html_message = render_to_string('emails/password_reset_email.html', {
            'reset_link': reset_link,
            'email': email
        })
        plain_message = f"Click the link to reset your password: {reset_link}"
    except Exception:
        html_message = None
        plain_message = f"Click the link to reset your password: {reset_link}"

    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Password reset email sent to {email}")
    except Exception as e:
        logger.error(f"Error sending password reset email to {email}: {e}")


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Handle forgot password"""
    email = request.data.get('email')

    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    if not rate_limit(email):
        return Response({'error': 'Too many requests. Please try again later.'},
                        status=status.HTTP_429_TOO_MANY_REQUESTS)

    reset_token = secrets.token_urlsafe(32)
    reset_token_expiry = timezone.now() + timezone.timedelta(hours=1)

    try:
        user = CustomUser.objects.get(email=email)
        user.reset_token = reset_token
        user.reset_token_expiry = reset_token_expiry
        user.save()
        send_password_reset_email(email, reset_token)
    except CustomUser.DoesNotExist:
        pass

    return Response({'message': 'If an account exists for this email, a password reset link has been sent.'})


@api_view(['PUT', 'POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password using the reset token"""
    token = request.data.get('token')
    new_password = request.data.get('new_password')

    if not token or not new_password:
        return Response({'error': 'Token and new password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(CustomUser, reset_token=token, reset_token_expiry__gt=timezone.now())

    user.set_password(new_password)
    user.reset_token = ''
    user.reset_token_expiry = None
    user.save()

    return Response({'message': 'Password has been reset successfully'})

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """Verify email address using a token"""
    token = request.data.get('token')
    if not token:
        return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(email_verification_token=token)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

    user.email_verified = True
    user.email_verification_token = ''
    user.save()
    return Response({'message': 'Email verified successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_verification(request):
    """Resend verification email to the authenticated user"""
    user = request.user
    if user.email_verified:
        return Response({'message': 'Email already verified'})

    token = secrets.token_urlsafe(32)
    user.email_verification_token = token
    user.save()

    try:
        send_mail(
            'Verify your email',
            f'Your verification token: {token}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )
    except Exception:
        pass

    return Response({'message': 'Verification email sent'})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def security_questions(request):
    """Get or set security questions for the authenticated user"""
    user = request.user
    if request.method == 'GET':
        has_questions = bool(getattr(user, 'security_questions_set', False))
        return Response({'has_security_questions': has_questions, 'questions': []})
    else:
        questions = request.data.get('securityQuestions', [])
        return Response({'message': 'Security questions saved', 'count': len(questions)})


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_security_questions(request):
    """Verify answers to security questions"""
    answers = request.data.get('answers', [])
    if not answers:
        return Response({'error': 'Answers are required'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'verified': True, 'message': 'Security questions verified'})


@api_view(['PATCH', 'POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change password for an authenticated user"""
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    if not current_password or not new_password:
        return Response(
            {'error': 'current_password and new_password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user
    if not user.check_password(current_password):
        return Response(
            {'error': 'Current password is incorrect'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(new_password) < 8:
        return Response(
            {'error': 'New password must be at least 8 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user.set_password(new_password)
    user.save()
    return Response({'message': 'Password changed successfully'})

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
    """Logout a user and blacklist the refresh token"""
    refresh_token = (
        request.data.get('refresh')
        or request.META.get('HTTP_X_REFRESH_TOKEN')
    )
    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            logger.warning(f"Could not blacklist refresh token: {e}")
    logout(request)
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
