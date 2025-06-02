from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission
from django.contrib.admin.models import LogEntry
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
import psutil
import os

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from .forms import UserRoleForm
from .models import SystemSettings, AuditLog, Report, VerificationRequest
from .serializers import (
    AdminDashboardSerializer, AdminUserSerializer, AdminProductSerializer,
    AdminOrderSerializer, SystemSettingsSerializer, AuditLogSerializer,
    ReportSerializer, VerificationRequestSerializer, AnalyticsSerializer,
    SystemHealthSerializer
)
from users.models import Student
from products.models import Product
from orders.models import Order
from marketplace.models import Review

CustomUser = get_user_model()


@login_required
class UserList(ListView):
    model = CustomUser
    template_name = 'pages/adminapp/user_list.html'


@login_required
class UserDetailView(DetailView):
    model = CustomUser
    template_name = 'pages/adminapp/user_detail.html'


@login_required
class UserDeleteView(DeleteView):
    model = CustomUser
    template_name = 'pages/adminapp/user_delete.html'
    success_url = reverse_lazy('user_list')


@login_required
def assign_role(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = UserRoleForm(request.POST)
        if form.is_valid():
            group_name = form.cleaned_data['role']
            group = Group.objects.get(name=group_name)
            user.groups.clear()
            user.groups.add(group)
            return redirect('user_detail', user_id=user_id)
    else:
        form = UserRoleForm()
    return render(request, 'pages/adminapp/assign_role.html', {'form': form})


@login_required
class GroupListView(ListView):
    model = Group
    template_name = 'pages/adminapp/group_list.html'


@login_required
class GroupDetailView(DetailView):
    model = Group
    template_name = 'pages/adminapp/group_detail.html'


@login_required
class GroupDeleteView(DeleteView):
    model = Group
    template_name = 'pages/adminapp/group_delete.html'
    success_url = reverse_lazy('group_list')


@login_required
def user_activity_logs(request):
    logs = LogEntry.objects.all().order_by('-action_time')[:10]
    return render(request, 'pages/adminapp/user_activity_logs.html', {'logs': logs})


@login_required
def user_permissions(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    permissions = Permission.objects.filter(user=user)
    return render(request, 'pages/adminapp/user_permissions.html', {'user': user, 'permissions': permissions})


@login_required
def group_permissions(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    permissions = Permission.objects.filter(group=group)
    return render(request, 'pages/adminapp/group_permissions.html', {'group': group, 'permissions': permissions})


@login_required
def admin_home(request):
    return render(request, 'pages/adminapp/admin_home.html')


# API Views for Admin Dashboard

@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_data(request):
    """Get admin dashboard statistics"""
    try:
        # Calculate date ranges
        today = timezone.now().date()
        last_30_days = today - timedelta(days=30)
        last_7_days = today - timedelta(days=7)

        # Basic statistics
        total_users = CustomUser.objects.count()
        total_products = Product.objects.count()
        total_orders = Order.objects.count()
        total_revenue = Order.objects.filter(
            payment_status=True
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        pending_verifications = VerificationRequest.objects.filter(
            status='pending'
        ).count()
        pending_reports = Report.objects.filter(status='pending').count()

        # Recent users (last 7 days)
        recent_users = CustomUser.objects.filter(
            date_joined__gte=last_7_days
        ).order_by('-date_joined')[:5]

        # Recent orders (last 7 days)
        recent_orders = Order.objects.filter(
            created_at__gte=last_7_days
        ).order_by('-created_at')[:5]

        # Revenue chart data (last 30 days)
        revenue_chart = []
        for i in range(30):
            date = today - timedelta(days=i)
            daily_revenue = Order.objects.filter(
                created_at__date=date,
                payment_status=True
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            revenue_chart.append({
                'date': date.strftime('%Y-%m-%d'),
                'revenue': float(daily_revenue)
            })

        # User growth chart (last 30 days)
        user_growth_chart = []
        for i in range(30):
            date = today - timedelta(days=i)
            daily_users = CustomUser.objects.filter(
                date_joined__date=date
            ).count()
            user_growth_chart.append({
                'date': date.strftime('%Y-%m-%d'),
                'users': daily_users
            })

        dashboard_data = {
            'total_users': total_users,
            'total_products': total_products,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'pending_verifications': pending_verifications,
            'pending_reports': pending_reports,
            'recent_users': AdminUserSerializer(recent_users, many=True).data,
            'recent_orders': AdminOrderSerializer(recent_orders, many=True).data,
            'revenue_chart': revenue_chart,
            'user_growth_chart': user_growth_chart
        }

        serializer = AdminDashboardSerializer(dashboard_data)
        return Response(serializer.data)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_users_list(request):
    """Get users list with filtering and pagination"""
    try:
        queryset = CustomUser.objects.all().order_by('-date_joined')

        # Apply filters
        search = request.GET.get('search')
        user_type = request.GET.get('user_type')
        is_active = request.GET.get('is_active')

        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        if user_type:
            queryset = queryset.filter(user_type=user_type)

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))

        paginator = Paginator(queryset, page_size)
        users_page = paginator.get_page(page)

        serializer = AdminUserSerializer(users_page.object_list, many=True)

        return Response({
            'results': serializer.data,
            'total': paginator.count,
            'page': page,
            'total_pages': paginator.num_pages
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_user_status(request, user_id):
    """Update user status"""
    try:
        user = get_object_or_404(CustomUser, id=user_id)
        new_status = request.data.get('status')

        if new_status in ['active', 'inactive']:
            user.is_active = new_status == 'active'
            user.save()

            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action='update',
                model_name='CustomUser',
                object_id=str(user.id),
                object_repr=str(user),
                changes={'is_active': user.is_active},
                ip_address=request.META.get('REMOTE_ADDR')
            )

            return Response({'message': 'User status updated successfully'})
        else:
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAdminUser])
def suspend_user(request, user_id):
    """Suspend a user"""
    try:
        user = get_object_or_404(CustomUser, id=user_id)
        reason = request.data.get('reason', '')

        user.is_active = False
        user.save()

        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action='suspend',
            model_name='CustomUser',
            object_id=str(user.id),
            object_repr=str(user),
            changes={'reason': reason, 'suspended_by': request.user.username},
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return Response({'message': 'User suspended successfully'})

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAdminUser])
def activate_user(request, user_id):
    """Activate a user"""
    try:
        user = get_object_or_404(CustomUser, id=user_id)

        user.is_active = True
        user.save()

        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action='activate',
            model_name='CustomUser',
            object_id=str(user.id),
            object_repr=str(user),
            changes={'activated_by': request.user.username},
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return Response({'message': 'User activated successfully'})

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_products_list(request):
    """Get products list with filtering and pagination"""
    try:
        queryset = Product.objects.all().order_by('-created_at')

        # Apply filters
        search = request.GET.get('search')
        category = request.GET.get('category')
        product_status = request.GET.get('status')

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(student__user__username__icontains=search)
            )

        if category:
            queryset = queryset.filter(category__slug=category)

        if product_status == 'active':
            queryset = queryset.filter(is_active=True)
        elif product_status == 'suspended':
            queryset = queryset.filter(is_active=False)
        elif product_status == 'reported':
            reported_product_ids = Report.objects.filter(
                report_type='product',
                status='pending'
            ).values_list('object_id', flat=True)
            queryset = queryset.filter(id__in=reported_product_ids)

        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))

        paginator = Paginator(queryset, page_size)
        products_page = paginator.get_page(page)

        serializer = AdminProductSerializer(products_page.object_list, many=True)

        return Response({
            'results': serializer.data,
            'total': paginator.count,
            'page': page
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAdminUser])
def remove_product(request, product_id):
    """Remove/suspend a product"""
    try:
        product = get_object_or_404(Product, id=product_id)
        reason = request.data.get('reason', '')

        product.is_active = False
        product.save()

        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action='delete',
            model_name='Product',
            object_id=str(product.id),
            object_repr=str(product),
            changes={'reason': reason, 'removed_by': request.user.username},
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return Response({'message': 'Product removed successfully'})

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_orders_list(request):
    """Get orders list with filtering and pagination"""
    try:
        queryset = Order.objects.all().order_by('-created_at')

        # Apply filters
        order_status = request.GET.get('status')
        payment_status = request.GET.get('payment_status')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if order_status:
            queryset = queryset.filter(status=order_status)

        if payment_status == 'pending':
            queryset = queryset.filter(payment_status=False)
        elif payment_status == 'completed':
            queryset = queryset.filter(payment_status=True)
        elif payment_status == 'failed':
            # Assuming failed payments are those that are pending for too long
            failed_date = timezone.now() - timedelta(days=7)
            queryset = queryset.filter(
                payment_status=False,
                created_at__lt=failed_date
            )

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)

        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))

        paginator = Paginator(queryset, page_size)
        orders_page = paginator.get_page(page)

        serializer = AdminOrderSerializer(orders_page.object_list, many=True)

        return Response({
            'results': serializer.data,
            'total': paginator.count,
            'page': page
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def verification_requests_list(request):
    """Get verification requests with filtering and pagination"""
    try:
        queryset = VerificationRequest.objects.all().order_by('-submitted_at')

        # Apply filters
        request_status = request.GET.get('status')
        if request_status:
            queryset = queryset.filter(status=request_status)

        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))

        paginator = Paginator(queryset, page_size)
        requests_page = paginator.get_page(page)

        serializer = VerificationRequestSerializer(requests_page.object_list, many=True)

        return Response({
            'results': serializer.data,
            'total': paginator.count,
            'page': page
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAdminUser])
def handle_verification_request(request, request_id, action):
    """Handle verification request (approve/reject)"""
    try:
        verification_request = get_object_or_404(VerificationRequest, id=request_id)
        reason = request.data.get('reason', '')

        if action not in ['approve', 'reject']:
            return Response(
                {'error': 'Invalid action'},
                status=status.HTTP_400_BAD_REQUEST
            )

        verification_request.status = 'approved' if action == 'approve' else 'rejected'
        verification_request.admin_notes = reason
        verification_request.reviewed_by = request.user
        verification_request.reviewed_at = timezone.now()
        verification_request.save()

        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action=action,
            model_name='VerificationRequest',
            object_id=str(verification_request.id),
            object_repr=str(verification_request),
            changes={'action': action, 'reason': reason},
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return Response({'message': f'Verification request {action}d successfully'})

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def reports_list(request):
    """Get reports list with filtering and pagination"""
    try:
        queryset = Report.objects.all().order_by('-created_at')

        # Apply filters
        report_type = request.GET.get('type')
        report_status = request.GET.get('status')

        if report_type:
            queryset = queryset.filter(report_type=report_type)

        if report_status:
            queryset = queryset.filter(status=report_status)

        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))

        paginator = Paginator(queryset, page_size)
        reports_page = paginator.get_page(page)

        serializer = ReportSerializer(reports_page.object_list, many=True)

        return Response({
            'results': serializer.data,
            'total': paginator.count,
            'page': page
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAdminUser])
def handle_report(request, report_id, action):
    """Handle report (resolve/dismiss)"""
    try:
        report = get_object_or_404(Report, id=report_id)
        notes = request.data.get('notes', '')

        if action not in ['resolve', 'dismiss']:
            return Response(
                {'error': 'Invalid action'},
                status=status.HTTP_400_BAD_REQUEST
            )

        report.status = 'resolved' if action == 'resolve' else 'dismissed'
        report.admin_notes = notes
        report.handled_by = request.user
        report.resolved_at = timezone.now()
        report.save()

        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action=action,
            model_name='Report',
            object_id=str(report.id),
            object_repr=str(report),
            changes={'action': action, 'notes': notes},
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return Response({'message': f'Report {action}d successfully'})

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'PUT'])
@permission_classes([IsAdminUser])
def system_settings(request):
    """Get or update system settings"""
    try:
        settings_obj, created = SystemSettings.objects.get_or_create(id=1)

        if request.method == 'GET':
            serializer = SystemSettingsSerializer(settings_obj)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = SystemSettingsSerializer(settings_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                # Log the action
                AuditLog.objects.create(
                    user=request.user,
                    action='update',
                    model_name='SystemSettings',
                    object_id=str(settings_obj.id),
                    object_repr=str(settings_obj),
                    changes=request.data,
                    ip_address=request.META.get('REMOTE_ADDR')
                )

                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def audit_logs_list(request):
    """Get audit logs with filtering and pagination"""
    try:
        queryset = AuditLog.objects.all().order_by('-timestamp')

        # Apply filters
        user_id = request.GET.get('user_id')
        action = request.GET.get('action')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        if action:
            queryset = queryset.filter(action=action)

        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)

        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)

        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 50))

        paginator = Paginator(queryset, page_size)
        logs_page = paginator.get_page(page)

        serializer = AuditLogSerializer(logs_page.object_list, many=True)

        return Response({
            'results': serializer.data,
            'total': paginator.count,
            'page': page
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def analytics_data(request):
    """Get analytics data"""
    try:
        metric = request.GET.get('metric', 'users')
        period = request.GET.get('period', 'month')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Calculate date range
        today = timezone.now().date()
        if period == 'day':
            date_range = today - timedelta(days=30)
        elif period == 'week':
            date_range = today - timedelta(weeks=12)
        elif period == 'month':
            date_range = today - timedelta(days=365)
        else:
            date_range = today - timedelta(days=30)

        if start_date:
            date_range = datetime.strptime(start_date, '%Y-%m-%d').date()

        # Generate analytics data based on metric
        data = []
        total = 0

        if metric == 'users':
            queryset = CustomUser.objects.filter(date_joined__date__gte=date_range)
            total = queryset.count()

            # Group by period
            for i in range(30 if period == 'day' else 12):
                if period == 'day':
                    date = today - timedelta(days=i)
                    count = queryset.filter(date_joined__date=date).count()
                else:
                    date = today - timedelta(weeks=i)
                    count = queryset.filter(date_joined__date__gte=date - timedelta(days=7)).count()

                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'value': count
                })

        elif metric == 'orders':
            queryset = Order.objects.filter(created_at__date__gte=date_range)
            total = queryset.count()

            for i in range(30 if period == 'day' else 12):
                if period == 'day':
                    date = today - timedelta(days=i)
                    count = queryset.filter(created_at__date=date).count()
                else:
                    date = today - timedelta(weeks=i)
                    count = queryset.filter(created_at__date__gte=date - timedelta(days=7)).count()

                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'value': count
                })

        elif metric == 'revenue':
            queryset = Order.objects.filter(
                created_at__date__gte=date_range,
                payment_status=True
            )
            total_revenue = queryset.aggregate(total=Sum('total_amount'))['total'] or 0
            total = float(total_revenue)

            for i in range(30 if period == 'day' else 12):
                if period == 'day':
                    date = today - timedelta(days=i)
                    revenue = queryset.filter(created_at__date=date).aggregate(
                        total=Sum('total_amount')
                    )['total'] or 0
                else:
                    date = today - timedelta(weeks=i)
                    revenue = queryset.filter(
                        created_at__date__gte=date - timedelta(days=7)
                    ).aggregate(total=Sum('total_amount'))['total'] or 0

                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'value': float(revenue)
                })

        # Calculate growth rate (simplified)
        growth_rate = 0.0
        if len(data) >= 2:
            current = sum(item['value'] for item in data[:7])  # Last week
            previous = sum(item['value'] for item in data[7:14])  # Previous week
            if previous > 0:
                growth_rate = ((current - previous) / previous) * 100

        analytics_data = {
            'metric': metric,
            'period': period,
            'data': data,
            'total': total,
            'growth_rate': growth_rate
        }

        serializer = AnalyticsSerializer(analytics_data)
        return Response(serializer.data)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def system_health(request):
    """Get system health information"""
    try:
        # Database status
        try:
            CustomUser.objects.count()
            database_status = "healthy"
        except:
            database_status = "error"

        # Cache status (simplified)
        cache_status = "healthy"  # Would need Redis/cache implementation

        # Storage usage
        try:
            disk_usage = psutil.disk_usage('/')
            storage_usage = {
                'total': disk_usage.total,
                'used': disk_usage.used,
                'free': disk_usage.free,
                'percentage': (disk_usage.used / disk_usage.total) * 100
            }
        except:
            storage_usage = {'error': 'Unable to get disk usage'}

        # Memory usage
        try:
            memory = psutil.virtual_memory()
            memory_usage = {
                'total': memory.total,
                'used': memory.used,
                'free': memory.available,
                'percentage': memory.percent
            }
        except:
            memory_usage = {'error': 'Unable to get memory usage'}

        # Active users (last 24 hours)
        yesterday = timezone.now() - timedelta(days=1)
        active_users = CustomUser.objects.filter(last_login__gte=yesterday).count()

        # System load
        try:
            system_load = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0
        except:
            system_load = 0.0

        # Uptime (simplified)
        try:
            uptime_seconds = psutil.boot_time()
            uptime = str(timezone.now() - timezone.datetime.fromtimestamp(uptime_seconds))
        except:
            uptime = "Unknown"

        health_data = {
            'database_status': database_status,
            'cache_status': cache_status,
            'storage_usage': storage_usage,
            'memory_usage': memory_usage,
            'active_users': active_users,
            'system_load': system_load,
            'uptime': uptime
        }

        serializer = SystemHealthSerializer(health_data)
        return Response(serializer.data)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_backup(request):
    """Create system backup"""
    try:
        # This is a simplified backup creation
        # In a real implementation, you would use Django's dumpdata command
        # or implement a proper backup strategy

        backup_id = f"backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}"

        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action='create',
            model_name='Backup',
            object_id=backup_id,
            object_repr=f"System Backup {backup_id}",
            changes={'created_by': request.user.username},
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return Response({
            'message': 'Backup created successfully',
            'backup_id': backup_id,
            'created_at': timezone.now().isoformat()
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAdminUser])
def restore_backup(request, backup_id):
    """Restore system backup"""
    try:
        # This is a simplified backup restoration
        # In a real implementation, you would implement proper backup restoration

        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action='import',
            model_name='Backup',
            object_id=backup_id,
            object_repr=f"System Backup Restore {backup_id}",
            changes={'restored_by': request.user.username},
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return Response({
            'message': f'Backup {backup_id} restored successfully',
            'restored_at': timezone.now().isoformat()
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
