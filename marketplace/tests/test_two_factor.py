from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Student
from ..utils.two_factor import (
    generate_totp_secret,
    verify_totp,
    generate_backup_codes,
    setup_2fa
)
import pyotp
import json

class TwoFactorAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.student = Student.objects.get(user=self.user)
        # Login the user
        self.client.login(username='testuser', password='testpass123')

    def test_enable_2fa(self):
        """Test enabling 2FA"""
        response = self.client.post(reverse('marketplace:enable-2fa'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('secret', data)
        self.assertIn('qr_code_url', data)
        self.assertIn('backup_codes', data)
        
        # Verify student model was updated
        self.student.refresh_from_db()
        self.assertTrue(self.student.two_factor_enabled)
        self.assertFalse(self.student.two_factor_verified)
        self.assertIsNotNone(self.student.two_factor_secret)

    def test_verify_2fa(self):
        """Test verifying 2FA token"""
        # Setup 2FA
        setup_data = setup_2fa(self.student)
        secret = setup_data['secret']
        
        # Generate valid token
        totp = pyotp.TOTP(secret)
        valid_token = totp.now()
        
        # Test verification
        response = self.client.post(reverse('marketplace:verify-2fa'), {
            'token': valid_token,
            'secret': secret
        })
        self.assertEqual(response.status_code, 200)
        
        # Verify student model was updated
        self.student.refresh_from_db()
        self.assertTrue(self.student.two_factor_verified)

    def test_invalid_token(self):
        """Test invalid 2FA token"""
        # Setup 2FA
        setup_data = setup_2fa(self.student)
        secret = setup_data['secret']
        
        # Test with invalid token
        response = self.client.post(reverse('marketplace:verify-2fa'), {
            'token': '000000',
            'secret': secret
        })
        self.assertEqual(response.status_code, 400)
        
        # Verify student model wasn't updated
        self.student.refresh_from_db()
        self.assertFalse(self.student.two_factor_verified)

    def test_backup_codes(self):
        """Test backup code functionality"""
        # Setup 2FA
        setup_data = setup_2fa(self.student)
        backup_codes = setup_data['backup_codes']
        
        # Test valid backup code
        response = self.client.post(reverse('marketplace:validate-backup-code'), {
            'code': backup_codes[0]
        })
        self.assertEqual(response.status_code, 200)
        
        # Verify code was consumed
        self.student.refresh_from_db()
        self.assertNotIn(backup_codes[0], self.student.backup_codes)

    def test_protected_routes(self):
        """Test protected route access with 2FA"""
        # Setup 2FA but don't verify
        setup_2fa(self.student)
        
        # Try accessing protected route
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 403)
        
        # Verify 2FA
        totp = pyotp.TOTP(self.student.two_factor_secret)
        self.client.post(reverse('marketplace:verify-2fa'), {
            'token': totp.now(),
            'secret': self.student.two_factor_secret
        })
        
        # Try accessing protected route again
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 200)

    def test_disable_2fa(self):
        """Test disabling 2FA"""
        # Setup and verify 2FA
        setup_data = setup_2fa(self.student)
        totp = pyotp.TOTP(setup_data['secret'])
        
        # Disable 2FA
        response = self.client.post(reverse('marketplace:disable-2fa'), {
            'token': totp.now()
        })
        self.assertEqual(response.status_code, 200)
        
        # Verify student model was updated
        self.student.refresh_from_db()
        self.assertFalse(self.student.two_factor_enabled)
        self.assertFalse(self.student.two_factor_verified)
        self.assertIsNone(self.student.two_factor_secret)
        self.assertEqual(len(self.student.backup_codes), 0)
