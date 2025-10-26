from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone

# Custom user manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# Custom user model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('customer', 'Customer'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=50, unique=True, db_index=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='student', db_index=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username', 'first_name']

    class Meta:
        db_table = 'custom_user'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['user_type']),
            models.Index(fields=['date_joined']),
        ]

    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_user_type_display_name(self):
        """Get the display name for user type"""
        return dict(self.USER_TYPES).get(self.user_type, self.user_type)

# UserProfile model
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')

    def __str__(self):
        return self.user.username

# Student model
class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    bio = models.TextField(blank=True, max_length=500)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    university = models.CharField(max_length=100, blank=True)
    student_id = models.CharField(max_length=20, blank=True, unique=True, null=True)
    
    # Two-factor authentication fields
    two_factor_enabled = models.BooleanField(default=False, db_index=True)
    two_factor_verified = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True, null=True)
    backup_codes = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_profile'
        indexes = [
            models.Index(fields=['two_factor_enabled']),
            models.Index(fields=['student_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.user.full_name} (Student)'
    
    @property
    def full_name(self):
        """Return the student's full name from user"""
        return self.user.full_name
    
    @property
    def email(self):
        """Return the student's email from user"""
        return self.user.email
    
    def generate_backup_codes(self, count=8):
        """Generate backup codes for 2FA recovery"""
        import random
        import string
        codes = []
        for _ in range(count):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            codes.append(code)
        self.backup_codes = codes
        self.save()
        return codes
    
    def verify_backup_code(self, code):
        """Verify and consume a backup code"""
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            self.save()
            return True
        return False
    
    def is_2fa_enabled(self):
        """Check if 2FA is enabled and verified"""
        return self.two_factor_enabled and self.two_factor_verified

# Signal to create profiles automatically
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_related_profiles(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        if instance.user_type == 'student':  # Only create Student profile if user is a student
            Student.objects.create(user=instance)
    else:
        # Only save userprofile if it exists
        try:
            if hasattr(instance, 'userprofile'):
                instance.userprofile.save()
        except UserProfile.DoesNotExist:
            pass
