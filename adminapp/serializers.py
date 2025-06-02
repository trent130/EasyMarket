from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta

from .models import SystemSettings, AuditLog, Report, VerificationRequest
from users.models import Student
from products.models import Product
from orders.models import Order
from marketplace.models import Review

CustomUser = get_user_model()


class AdminDashboardSerializer(serializers.Serializer):
    """Serializer for admin dashboard data"""
    total_users = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_verifications = serializers.IntegerField()
    pending_reports = serializers.IntegerField()
    recent_users = serializers.ListField()
    recent_orders = serializers.ListField()
    revenue_chart = serializers.ListField()
    user_growth_chart = serializers.ListField()


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for user management"""
    full_name = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()
    orders_count = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    last_login_display = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'user_type', 'is_active', 'is_staff',
            'date_joined', 'last_login', 'last_login_display',
            'products_count', 'orders_count', 'total_spent'
        ]
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    
    def get_products_count(self, obj):
        try:
            return obj.student.products.count()
        except:
            return 0
    
    def get_orders_count(self, obj):
        return obj.order_set.count()
    
    def get_total_spent(self, obj):
        total = obj.order_set.aggregate(total=Sum('total_amount'))['total']
        return float(total) if total else 0.0
    
    def get_last_login_display(self, obj):
        if obj.last_login:
            return obj.last_login.strftime('%Y-%m-%d %H:%M')
        return 'Never'


class AdminProductSerializer(serializers.ModelSerializer):
    """Serializer for product management"""
    student_name = serializers.CharField(source='student.user.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    reports_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'price', 'student', 'student_name',
            'category', 'category_name', 'condition', 'stock',
            'is_active', 'created_at', 'views_count', 'total_sales',
            'reports_count'
        ]
    
    def get_reports_count(self, obj):
        return Report.objects.filter(
            report_type='product',
            object_id=str(obj.id),
            status='pending'
        ).count()


class AdminOrderSerializer(serializers.ModelSerializer):
    """Serializer for order management"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'reference', 'user', 'user_name', 'total_amount',
            'status', 'payment_method', 'payment_status',
            'created_at', 'updated_at', 'items_count'
        ]
    
    def get_items_count(self, obj):
        return obj.orderitem_set.count()


class SystemSettingsSerializer(serializers.ModelSerializer):
    """Serializer for system settings"""
    class Meta:
        model = SystemSettings
        fields = [
            'maintenance_mode', 'registration_enabled', 'max_file_size',
            'allowed_file_types', 'notification_settings', 'site_name',
            'contact_email', 'contact_phone', 'updated_at'
        ]


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'model_name',
            'object_id', 'object_repr', 'changes', 'ip_address',
            'timestamp'
        ]


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for reports"""
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    handled_by_name = serializers.CharField(source='handled_by.username', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'reporter', 'reporter_name', 'report_type', 'object_id',
            'reason', 'status', 'admin_notes', 'handled_by', 'handled_by_name',
            'created_at', 'resolved_at'
        ]


class VerificationRequestSerializer(serializers.ModelSerializer):
    """Serializer for verification requests"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.username', read_only=True)
    
    class Meta:
        model = VerificationRequest
        fields = [
            'id', 'user', 'user_name', 'document_type', 'document_file',
            'additional_info', 'status', 'admin_notes', 'reviewed_by',
            'reviewed_by_name', 'submitted_at', 'reviewed_at'
        ]


class AnalyticsSerializer(serializers.Serializer):
    """Serializer for analytics data"""
    metric = serializers.CharField()
    period = serializers.CharField()
    data = serializers.ListField()
    total = serializers.IntegerField()
    growth_rate = serializers.FloatField()


class SystemHealthSerializer(serializers.Serializer):
    """Serializer for system health data"""
    database_status = serializers.CharField()
    cache_status = serializers.CharField()
    storage_usage = serializers.DictField()
    memory_usage = serializers.DictField()
    active_users = serializers.IntegerField()
    system_load = serializers.FloatField()
    uptime = serializers.CharField()
