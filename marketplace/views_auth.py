from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
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
import pyotp
import base64

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