from django.conf import settings

# M-Pesa Configuration
MPESA_ENVIRONMENT = getattr(settings, 'MPESA_ENVIRONMENT', 'sandbox')
MPESA_CONSUMER_KEY = getattr(settings, 'MPESA_CONSUMER_KEY', '')
MPESA_CONSUMER_SECRET = getattr(settings, 'MPESA_CONSUMER_SECRET', '')
MPESA_SHORTCODE = getattr(settings, 'MPESA_SHORTCODE', '')
MPESA_PASSKEY = getattr(settings, 'MPESA_PASSKEY', '')
MPESA_INITIATOR_NAME = getattr(settings, 'MPESA_INITIATOR_NAME', '')
MPESA_SECURITY_CREDENTIAL = getattr(settings, 'MPESA_SECURITY_CREDENTIAL', '')

# API Endpoints
if MPESA_ENVIRONMENT == 'sandbox':
    MPESA_BASE_URL = 'https://sandbox.safaricom.co.ke'
else:
    MPESA_BASE_URL = 'https://api.safaricom.co.ke'

MPESA_AUTH_URL = f'{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials'
MPESA_STK_PUSH_URL = f'{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest'
MPESA_QUERY_URL = f'{MPESA_BASE_URL}/mpesa/stkpushquery/v1/query'
MPESA_REVERSAL_URL = f'{MPESA_BASE_URL}/mpesa/reversal/v1/request'

# Callback URLs
MPESA_CALLBACK_BASE_URL = getattr(settings, 'PAYMENT_HOST', 'http://localhost:8000')
MPESA_CALLBACK_URLS = {
    'stk_push': f'{MPESA_CALLBACK_BASE_URL}/api/payment/mpesa-callback/',
    'reversal': f'{MPESA_CALLBACK_BASE_URL}/api/payment/reversal-callback/',
    'timeout': f'{MPESA_CALLBACK_BASE_URL}/api/payment/timeout-callback/'
}

# Payment Settings
PAYMENT_METHODS = {
    'mpesa': {
        'enabled': True,
        'display_name': 'M-Pesa',
        'description': 'Pay with M-Pesa mobile money',
        'min_amount': 10,  # Minimum amount in KES
        'max_amount': 150000,  # Maximum amount in KES
        'currency': 'KES'
    },
    'card': {
        'enabled': False,
        'display_name': 'Credit/Debit Card',
        'description': 'Pay with credit or debit card',
        'supported_cards': ['visa', 'mastercard'],
        'currency': 'USD'
    },
    'bank': {
        'enabled': False,
        'display_name': 'Bank Transfer',
        'description': 'Pay via bank transfer',
        'currency': 'KES'
    }
}

# Transaction Settings
TRANSACTION_TYPES = {
    'payment': {
        'code': 'CustomerPayBillOnline',
        'description': 'Customer Pay Bill Online'
    },
    'refund': {
        'code': 'TransactionReversal',
        'description': 'Transaction Reversal'
    }
}

# Validation Settings
PHONE_NUMBER_VALIDATION = {
    'country_code': '254',  # Kenya
    'length': 12,  # Including country code
    'formats': [
        '^254[17][0-9]{8}$',  # Safaricom and Airtel
    ]
}

# Error Messages
ERROR_MESSAGES = {
    'invalid_phone': 'Invalid phone number format. Use format: 254XXXXXXXXX',
    'amount_too_low': 'Amount is below minimum allowed',
    'amount_too_high': 'Amount exceeds maximum allowed',
    'payment_failed': 'Payment processing failed. Please try again',
    'payment_cancelled': 'Payment was cancelled by user',
    'payment_timeout': 'Payment request timed out',
    'invalid_currency': 'Invalid currency for selected payment method'
}

# Retry Settings
RETRY_SETTINGS = {
    'max_attempts': 3,
    'backoff_factor': 2,  # seconds
    'status_check_interval': 5,  # seconds
    'timeout': 60  # seconds
}

# Cache Settings
CACHE_SETTINGS = {
    'access_token_key': 'mpesa_access_token',
    'access_token_timeout': 3000,  # 50 minutes
    'transaction_timeout': 300,  # 5 minutes
}

# Notification Settings
NOTIFICATION_SETTINGS = {
    'payment_success': {
        'sms': True,
        'email': True,
        'push': True
    },
    'payment_failed': {
        'sms': True,
        'email': True,
        'push': True
    },
    'refund_initiated': {
        'sms': True,
        'email': True,
        'push': True
    }
}
