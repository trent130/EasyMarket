from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_payment_confirmation_email(transaction):
    """Send payment confirmation email to customer."""
    try:
        context = {
            'user': transaction.user,
            'transaction': transaction,
            'support_email': settings.SUPPORT_EMAIL,
            'support_phone': settings.SUPPORT_PHONE
        }

        # Render email templates
        html_message = render_to_string('emails/payment_confirmation.html', context)
        plain_message = render_to_string('emails/payment_confirmation.txt', context)

        send_mail(
            subject=f'Payment Confirmation - {transaction.transaction_id}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[transaction.user.email],
            html_message=html_message
        )

        logger.info(f"Payment confirmation email sent for transaction {transaction.transaction_id}")
        
    except Exception as e:
        logger.error(f"Error sending payment confirmation email: {str(e)}")

def send_payment_failed_email(transaction):
    """Send payment failed notification to customer."""
    try:
        context = {
            'user': transaction.user,
            'transaction': transaction,
            'support_email': settings.SUPPORT_EMAIL,
            'support_phone': settings.SUPPORT_PHONE
        }

        html_message = render_to_string('emails/payment_failed.html', context)
        plain_message = render_to_string('emails/payment_failed.txt', context)

        send_mail(
            subject=f'Payment Failed - {transaction.transaction_id}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[transaction.user.email],
            html_message=html_message
        )

        logger.info(f"Payment failed email sent for transaction {transaction.transaction_id}")
        
    except Exception as e:
        logger.error(f"Error sending payment failed email: {str(e)}")