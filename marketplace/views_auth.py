from rest_framework import status, exceptions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Student
from .serializers import (
    TwoFactorEnableSerializer,
    TwoFactorVerifySerializer,
    TwoFactorStatusSerializer,
    TwoFactorDisableSerializer,
    BackupCodesSerializer,
    ValidateBackupCodeSerializer
)
import logging
import pyotp
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone  # Import timezone

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
    """Enable 2FA for a user"""
    user = get_object_or_404(User, id=request.data.get('user_id'))

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
    username_or_email = request.data.get('username_or_email')
    password = request.data.get('password')

    if '@' in username_or_email:
        try:
            user = User.objects.get(email=username_or_email)
            username = user.username
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        username = username_or_email
        
    user = authenticate(request, username=username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
    
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """Sign up a new user"""
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password, email=email)
    Student.objects.create(user=user)

    return Response({'message': 'Sign up successful'}, status=status.HTTP_201_CREATED)

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
    user = get_object_or_404(User, id=request.user.id)

    if not user.isTwoFactorEnabled:
        return Response({'error': 'Two-factor authentication is not enabled'}, status=status.HTTP_400_BAD_REQUEST)

    user.isTwoFactorEnabled = False
    user.twoFactorSecret = None
    user.save()

    return Response({'message': 'Two-factor authentication has been disabled'})

@api_view(['POST'])
@permission_classes([AllowAny])
async def forgot_password(request):
    """Handle forgot password"""
    email = request.data.get('email')

    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    if not rate_limit(email):
        return Response({'error': 'Too many requests. Please try again later.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    reset_token = crypto.randomBytes(20).toString('hex')
    reset_token_expiry = timezone.now() + timezone.timedelta(hours=1)  # 1 hour from now

    user = get_object_or_404(User, email=email)
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

    user = get_object_or_404(User, resetToken=token, resetTokenExpiry__gt=timezone.now())

    hashed_password = await hash(new_password, 10)
    user.password = hashed_password
    user.resetToken = None
    user.resetTokenExpiry = None
    user.save()

    return Response({'message': 'Password has been reset successfully'})

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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_backup_codes(request):
    """Regenerate backup codes for 2FA"""
    student = get_object_or_404(Student, user=request.user)
    
    if not student.two_factor_enabled:
        return Response({'error': '2FA is not enabled'}, status=status.HTTP_400_BAD_REQUEST)

    backup_codes = student.generate_backup_codes()
    serializer = BackupCodesSerializer(data={'codes': backup_codes})
    if serializer.is_valid():
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            data['user_id'] = self.user.id
            data['email'] = self.user.email
            return data
        except Exception as e:
            logger.error(f"Token generation error: {str(e)}")
            raise

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data)
        except Exception as e:
            logger.error(f"Unexpected token generation error: {str(e)}")
            return Response({'error': 'Authentication failed', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         return Response({'success': True})
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signout(request):
    """Logout a user"""
    # TODO: Implement logout logic here
    user = request.user
    logout(request, user)
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


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