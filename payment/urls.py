from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()
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

]
