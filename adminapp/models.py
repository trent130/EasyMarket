from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.

class SystemSettings(models.Model):
    """System-wide settings"""
    maintenance_mode = models.BooleanField(default=False)
    registration_enabled = models.BooleanField(default=True)
    max_file_size = models.IntegerField(default=5242880)  # 5MB in bytes
    allowed_file_types = models.JSONField(default=list)
    notification_settings = models.JSONField(default=dict)
    site_name = models.CharField(max_length=100, default="Student Marketplace")
    contact_email = models.EmailField(default="admin@example.com")
    contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return f"System Settings - {self.site_name}"


class AuditLog(models.Model):
    """Audit log for tracking admin actions"""
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('suspend', 'Suspend'),
        ('activate', 'Activate'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('view', 'View'),
        ('export', 'Export'),
        ('import', 'Import'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['model_name', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.model_name} - {self.timestamp}"


class Report(models.Model):
    """User reports for content moderation"""
    REPORT_TYPES = [
        ('user', 'User'),
        ('product', 'Product'),
        ('review', 'Review'),
        ('message', 'Message'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports_made'
    )
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    object_id = models.CharField(max_length=100)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_handled'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['report_type', 'status']),
        ]

    def __str__(self):
        return f"Report #{self.id} - {self.report_type} - {self.status}"


class VerificationRequest(models.Model):
    """User verification requests"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50)
    document_file = models.FileField(upload_to='verification_documents/')
    additional_info = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verifications_reviewed'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['status', 'submitted_at']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"Verification #{self.id} - {self.user.username} - {self.status}"
