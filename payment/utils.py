import re
import json
import hashlib
from decimal import Decimal
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from .config import (
    PAYMENT_METHODS,
    PHONE_NUMBER_VALIDATION,
    ERROR_MESSAGES,
    CACHE_SETTINGS,
    NOTIFICATION_SETTINGS
)
from .models import Transaction
import logging

logger = logging.getLogger(__name__)

def validate_phone_number(phone_number: str) -> tuple[bool, str]:
    """Validate phone number format"""
    # Remove any spaces or special characters
    cleaned = ''.join(filter(str.isdigit, phone_number))
    
    # Check country code and length
    if not cleaned.startswith(PHONE_NUMBER_VALIDATION['country_code']):
        return False, ERROR_MESSAGES['invalid_phone']
        
    if len(cleaned) != PHONE_NUMBER_VALIDATION['length']:
        return False, ERROR_MESSAGES['invalid_phone']
        
    # Check against allowed formats
    for pattern in PHONE_NUMBER_VALIDATION['formats']:
        if re.match(pattern, cleaned):
            return True, cleaned
            
    return False, ERROR_MESSAGES['invalid_phone']

def validate_payment_amount(amount: Decimal, payment_method: str) -> tuple[bool, str]:
    """Validate payment amount for given payment method"""
    method_config = PAYMENT_METHODS.get(payment_method)
    if not method_config:
        return False, "Invalid payment method"
        
    if amount < method_config['min_amount']:
        return False, ERROR_MESSAGES['amount_too_low']
        
    if amount > method_config['max_amount']:
        return False, ERROR_MESSAGES['amount_too_high']
        
    return True, ""

def generate_transaction_id() -> str:
    """Generate unique transaction ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:6]
    return f"TXN{timestamp}{random}"

def cache_transaction_data(transaction_id: str, data: dict, timeout: int = None) -> None:
    """Cache transaction data"""
    if timeout is None:
        timeout = CACHE_SETTINGS['transaction_timeout']
    
    cache_key = f"transaction_{transaction_id}"
    cache.set(cache_key, json.dumps(data), timeout)

def get_cached_transaction_data(transaction_id: str) -> dict:
    """Retrieve cached transaction data"""
    cache_key = f"transaction_{transaction_id}"
    data = cache.get(cache_key)
    return json.loads(data) if data else None

def format_currency(amount: Decimal, currency: str = 'KES') -> str:
    """Format currency amount"""
    return f"{currency} {amount:,.2f}"

def calculate_transaction_fee(amount: Decimal, payment_method: str) -> Decimal:
    """Calculate transaction fee based on amount and payment method"""
    method_config = PAYMENT_METHODS.get(payment_method)
    if not method_config:
        return Decimal('0')
        
    # Example fee calculation (implement your own logic)
    if payment_method == 'mpesa':
        if amount <= 100:
            return Decimal('0')
        elif amount <= 1000:
            return Decimal('15')
        else:
            return amount * Decimal('0.02')  # 2% fee
            
    return Decimal('0')

def send_payment_notification(transaction: Transaction, notification_type: str) -> None:
    """Send payment notification based on settings"""
    settings = NOTIFICATION_SETTINGS.get(notification_type, {})
    
    try:
        if settings.get('sms'):
            send_sms_notification(transaction)
            
        if settings.get('email'):
            send_email_notification(transaction)
            
        if settings.get('push'):
            send_push_notification(transaction)
            
    except Exception as e:
        logger.error(f"Notification error for transaction {transaction.id}: {str(e)}")

def send_sms_notification(transaction: Transaction) -> None:
    """Send SMS notification"""
    # Implement SMS sending logic
    pass

def send_email_notification(transaction: Transaction) -> None:
    """Send email notification"""
    # Implement email sending logic
    pass

def send_push_notification(transaction: Transaction) -> None:
    """Send push notification"""
    # Implement push notification logic
    pass

def get_payment_status(transaction_id: str) -> dict:
    """Get comprehensive payment status"""
    try:
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        return {
            'status': transaction.status,
            'amount': transaction.amount,
            'currency': transaction.currency,
            'payment_method': transaction.payment_method,
            'created_at': transaction.created_at,
            'updated_at': transaction.updated_at,
            'is_completed': transaction.status == 'completed',
            'payment_details': transaction.payment_details
        }
    except Transaction.DoesNotExist:
        return None

def validate_currency_conversion(amount: Decimal, from_currency: str, to_currency: str) -> tuple[Decimal, str]:
    """Validate and convert currency"""
    # Implement currency conversion logic
    # For now, assuming only KES is supported
    if from_currency != 'KES' or to_currency != 'KES':
        return None, ERROR_MESSAGES['invalid_currency']
    return amount, ""

def is_payment_expired(transaction: Transaction) -> bool:
    """Check if payment has expired"""
    expiry_time = transaction.created_at + timedelta(
        seconds=CACHE_SETTINGS['transaction_timeout']
    )
    return datetime.now() > expiry_time

def generate_payment_receipt(transaction: Transaction) -> dict:
    """Generate payment receipt data"""
    return {
        'receipt_number': f"RCP{transaction.transaction_id}",
        'date': transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'amount': format_currency(transaction.amount, transaction.currency),
        'payment_method': transaction.get_payment_method_display(),
        'status': transaction.get_status_display(),
        'customer_name': f"{transaction.order.user.first_name} {transaction.order.user.last_name}",
        'customer_phone': transaction.payment_details.get('phone_number'),
        'order_reference': f"Order #{transaction.order.id}",
        'merchant_name': settings.BUSINESS_NAME,
        'merchant_contact': settings.BUSINESS_CONTACT
    }
