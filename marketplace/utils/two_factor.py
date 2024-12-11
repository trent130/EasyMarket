import pyotp
import qrcode
import io
import base64
from django.conf import settings
from ..models import Student


def generate_totp_secret():
    """Generate a new TOTP secret key"""
    return pyotp.random_base32()


def generate_totp(secret):
    """Create a TOTP object for a given secret"""
    return pyotp.TOTP(secret)


def verify_totp(secret, token):
    """Verify a TOTP token"""
    totp = pyotp.TOTP(secret)
    return totp.verify(token)


def generate_qr_code(secret, email):
    """Generate a QR code for the TOTP secret"""
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        email,
        issuer_name=settings.TWO_FACTOR_SETTINGS.get('ISSUER_NAME', 'EasyMarket')
    )

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(provisioning_uri)
    qr.make(fit=True)

    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"


def generate_backup_codes(count=8):
    """Generate a list of backup codes"""
    import random
    import string
    
    codes = []
    for _ in range(count):
        # Generate 8-character code with uppercase letters and numbers
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        codes.append(code)
    return codes


def is_path_protected(path):
    """Check if a path requires 2FA verification"""
    protected_paths = settings.TWO_FACTOR_SETTINGS.get('PROTECTED_PATHS', [])
    return any(path.startswith(protected) for protected in protected_paths)


def requires_2fa(user):
    """Check if a user requires 2FA verification"""
    try:
        student = Student.objects.get(user=user)
        return student.two_factor_enabled and not student.two_factor_verified
    except Student.DoesNotExist:
        return False


def verify_backup_code(student, code):
    """Verify and consume a backup code"""
    if code in student.backup_codes:
        student.backup_codes.remove(code)
        student.save()
        return True
    return False


def setup_2fa(student):
    """Set up 2FA for a student"""
    secret = generate_totp_secret()
    backup_codes = generate_backup_codes(
        count=settings.TWO_FACTOR_SETTINGS.get('BACKUP_CODES_COUNT', 8)
    )
    
    student.two_factor_secret = secret
    student.two_factor_enabled = True
    student.two_factor_verified = False
    student.backup_codes = backup_codes
    student.save()
    
    qr_code = generate_qr_code(secret, student.email)
    
    return {
        'secret': secret,
        'qr_code_url': qr_code,
        'backup_codes': backup_codes
    }


def disable_2fa(student):
    """Disable 2FA for a student"""
    student.two_factor_enabled = False
    student.two_factor_verified = False
    student.two_factor_secret = None
    student.backup_codes = []
    student.save()
