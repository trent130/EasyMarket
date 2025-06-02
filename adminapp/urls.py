from django.urls import path
from . import views

urlpatterns = [
    # Traditional admin views
    path('', views.admin_home, name='admin_home'),
    path('web/users/', views.UserList, name='user_list'),
    path('web/users/<int:pk>/', views.UserDetailView, name='user_detail'),
    path('web/users/<int:pk>/delete/', views.UserDeleteView, name='user_delete'),
    path('web/users/<int:pk>/assign_role/', views.assign_role, name='assign_role'),
    path('web/groups/', views.GroupListView, name='group_list'),
    path('web/groups/<int:pk>/', views.GroupDetailView, name='group_detail'),
    path('web/groups/<int:pk>/delete/', views.GroupDeleteView, name='group_delete'),
    path('web/activity_logs/', views.user_activity_logs, name='user_activity_logs'),
    path('web/users/<int:pk>/permissions/', views.user_permissions, name='user_permissions'),
    path('web/groups/<int:pk>/permissions/', views.group_permissions, name='group_permissions'),

    # API endpoints for admin dashboard
    path('dashboard/', views.dashboard_data, name='admin_dashboard_api'),

    # User management API endpoints
    path('users/', views.admin_users_list, name='admin_users_api'),
    path('users/<str:user_id>/status/', views.update_user_status, name='admin_user_status'),
    path('users/<str:user_id>/suspend/', views.suspend_user, name='admin_suspend_user'),
    path('users/<str:user_id>/activate/', views.activate_user, name='admin_activate_user'),

    # Product management API endpoints
    path('products/', views.admin_products_list, name='admin_products_api'),
    path('products/<int:product_id>/remove/', views.remove_product, name='admin_remove_product'),

    # Order management API endpoints
    path('orders/', views.admin_orders_list, name='admin_orders_api'),

    # Verification requests API endpoints
    path('verifications/', views.verification_requests_list, name='admin_verifications_api'),
    path('verifications/<int:request_id>/<str:action>/', views.handle_verification_request, name='admin_handle_verification'),

    # Reports management API endpoints
    path('reports/', views.reports_list, name='admin_reports_api'),
    path('reports/<int:report_id>/<str:action>/', views.handle_report, name='admin_handle_report'),

    # System settings API endpoints
    path('settings/', views.system_settings, name='admin_settings_api'),

    # Audit logs API endpoints
    path('audit-logs/', views.audit_logs_list, name='admin_audit_logs_api'),

    # Analytics API endpoints
    path('analytics/', views.analytics_data, name='admin_analytics_api'),

    # System health and backup API endpoints
    path('system/health/', views.system_health, name='admin_system_health'),
    path('system/backup/', views.create_backup, name='admin_create_backup'),
    path('system/restore/<str:backup_id>/', views.restore_backup, name='admin_restore_backup'),
]
