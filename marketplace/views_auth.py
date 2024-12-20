from rest_framework import status
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
# import base64

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
    """Enable 2FA for a user"""
    serializer = TwoFactorEnableSerializer(data={'user_id': request.user.id})
    if serializer.is_valid():
        student = get_object_or_404(Student, user=request.user)
        
        # Generate secret key
        secret = pyotp.random_base32()
        student.two_factor_secret = secret
        student.two_factor_enabled = True
        student.two_factor_verified = False
        student.save()

        # Generate QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            student.email,
            issuer_name="EasyMarket"
        )

        # Generate backup codes
        backup_codes = student.generate_backup_codes()

        return Response({
            'secret': secret,
            'qr_code_url': provisioning_uri,
            'backup_codes': backup_codes
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def signin(request):
    """Sign in a user"""
    username_or_email = request.data.get('username_or_email')
    """ username = User.objects.filter(username=username_or_email).first().username """
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
        if refresh:
            # TODO: Implement refresh token logic here
            return Response({'refresh': str(refresh),
                            'access': str(refresh.access_token)},
                            status=status.HTTP_200_OK
                            )
        return Response({'message': 'Sign in successful'}, status=status.HTTP_200_OK)
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
    Student.objects.create(user=user)  # Assuming a Student model is linked to User

    return Response({'message': 'Sign up successful'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa(request):
    """Verify 2FA token"""
    student = get_object_or_404(Student, user=request.user)
    
    if not student.two_factor_enabled:
        return Response(
            {'error': '2FA is not enabled'},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = TwoFactorVerifySerializer(data=request.data)
    if serializer.is_valid():
        if student.two_factor_secret != serializer.validated_data['secret']:
            return Response(
                {'error': 'Invalid secret'},
                status=status.HTTP_400_BAD_REQUEST
            )

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
        return Response(
            {'error': '2FA is not enabled'},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = TwoFactorDisableSerializer(data=request.data)
    if serializer.is_valid():
        totp = pyotp.TOTP(student.two_factor_secret)
        if not totp.verify(serializer.validated_data['token']):
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )

        student.two_factor_enabled = False
        student.two_factor_verified = False
        student.two_factor_secret = None
        student.backup_codes = []
        student.save()

        return Response({'success': True})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Handle forgot password"""
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        # Generate a password reset token and send email logic here
        return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_backup_code(request):
    """Validate a backup code for 2FA recovery"""
    student = get_object_or_404(Student, user=request.user)
    
    if not student.two_factor_enabled:
        return Response(
            {'error': '2FA is not enabled'},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = ValidateBackupCodeSerializer(data=request.data)
    if serializer.is_valid():
        if student.verify_backup_code(serializer.validated_data['code']):
            return Response({'success': True})
        return Response(
            {'error': 'Invalid backup code'},
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def disable_backup_code(request):
#     """Disable backup codes for 2FA"""
#     student = get_object_or_404(Student, user=request.user)
    
#     if not student.two_factor_enabled:
#         return Response(
#             {'error': '2FA is not enabled'},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     serializer = BackupCodesSerializer(data=request.data)
#     if serializer.is_valid():
#         student.backup_codes = []
#         student.save()
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