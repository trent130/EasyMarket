from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

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
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='student')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username', 'first_name']

    class Meta:
        db_table = 'custom_user'

    def __str__(self):
        return self.email

# UserProfile model
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')

    def __str__(self):
        return self.user.username

# Student model
class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

# Signal to create profiles automatically
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_related_profiles(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        if instance.user_type == 'student':  # Only create Student profile if user is a student
            Student.objects.create(user=instance, email=instance.email)
    else:
        instance.userprofile.save()
