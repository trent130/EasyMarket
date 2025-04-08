from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.conf import settings

router = DefaultRouter()
router.register(r'transactions', views.PaymentViewSet, basename='transaction')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # M-Pesa Payment URLs
    path('mpesa/',
         views.PaymentViewSet.as_view({'post': 'mpesa'}),
         name='mpesa-payment'),
    path('verify/',
         views.PaymentViewSet.as_view({'post': 'verify_payment'}),
         name='verify-payment'),
    path('mpesa-callback/',
         views.mpesa_callback,
         name='mpesa-callback'),

    # Transaction Management
    path('transactions/<str:transaction_id>/refund/',
         views.PaymentViewSet.as_view({'post': 'refund'}),
         name='refund-payment'),
    path('transactions/<str:transaction_id>/receipt/',
         views.PaymentViewSet.as_view({'get': 'receipt'}),
         name='payment-receipt'),

    # Payment History
    path('history/',
         views.PaymentViewSet.as_view({'get': 'history'}),
         name='payment-history'),

    # Webhook URLs for payment service callbacks
    path('webhooks/mpesa/confirmation/',
         views.mpesa_callback,
         name='mpesa-confirmation'),
    path('webhooks/mpesa/validation/',
         views.mpesa_callback,
         name='mpesa-validation'),
    path('webhooks/mpesa/reversal/',
         views.mpesa_callback,
         name='mpesa-reversal'),

    # Payment Method Management
    path('methods/',
         views.PaymentViewSet.as_view({
             'get': 'list_payment_methods',
             'post': 'add_payment_method'
         }),
         name='payment-methods'),
    path('methods/<int:pk>/',
         views.PaymentViewSet.as_view({
             'delete': 'remove_payment_method',
             'put': 'update_payment_method'
         }),
         name='payment-method-detail'),
    path('methods/<int:pk>/set-default/',
         views.PaymentViewSet.as_view({'post': 'set_default_payment_method'}),
         name='set-default-payment-method'),

    # Payment Settings
    path('settings/',
         views.PaymentViewSet.as_view({
             'get': 'get_payment_settings',
             'put': 'update_payment_settings'
         }),
         name='payment-settings'),

    # Payment Analytics
    path('analytics/',
         views.PaymentViewSet.as_view({'get': 'get_payment_analytics'}),
         name='payment-analytics'),
    path('analytics/export/',
         views.PaymentViewSet.as_view({'get': 'export_payment_analytics'}),
         name='export-payment-analytics'),

    # System Status
    path('system-status/',
         views.PaymentViewSet.as_view({'get': 'get_system_status'}),
         name='payment-system-status'),
]

# Add debug patterns if in debug mode
if settings.DEBUG:
    urlpatterns += [
        # Test payment endpoints
        path('api/payment/test/mpesa/',
             views.PaymentViewSet.as_view({'post': 'test_mpesa_payment'}),
             name='test-mpesa-payment'),
        path('api/payment/test/callback/',
             views.PaymentViewSet.as_view({'post': 'test_payment_callback'}),
             name='test-payment-callback'),
    ]
