import requests
import base64
import json
from datetime import datetime
from requests.auth import HTTPBasicAuth
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class MpesaClient:
    def __init__(self):
        self.business_shortcode = settings.MPESA_BUSINESS_SHORTCODE
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.passkey = settings.MPESA_PASSKEY
        
        # API endpoints
        self.access_token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        self.stk_push_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        self.query_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query'
        
        # Get access token on initialization
        self.access_token = self._get_access_token()

    def _get_access_token(self):
        """Get OAuth access token from Safaricom"""
        try:
            response = requests.get(
                self.access_token_url,
                auth=HTTPBasicAuth(
                    self.consumer_key,
                    self.consumer_secret
                )
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('access_token')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting access token: {str(e)}")
            raise

    def _generate_password(self):
        """Generate password for STK push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{self.business_shortcode}{self.passkey}{timestamp}"
        password_bytes = password_str.encode('ascii')
        return base64.b64encode(password_bytes).decode('utf-8'), timestamp

    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK push payment request"""
        try:
            password, timestamp = self._generate_password()
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": phone_number,
                "PartyB": self.business_shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": f"{settings.PAYMENT_HOST}/api/payment/mpesa-callback/",
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }
            
            response = requests.post(
                self.stk_push_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"STK push error: {str(e)}")
            raise

    def check_payment_status(self, checkout_request_id):
        """Check status of STK push payment"""
        try:
            password, timestamp = self._generate_password()
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            response = requests.post(
                self.query_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            result_code = result.get('ResultCode')
            
            if result_code == "0":
                return "completed"
            elif result_code == "1037":  # Timeout
                return "timeout"
            elif result_code == "1032":  # Cancelled
                return "cancelled"
            else:
                return "failed"
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Payment status check error: {str(e)}")
            raise

    def process_refund(self, transaction_id, amount, remarks):
        """Process M-Pesa refund"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "InitiatorName": settings.MPESA_INITIATOR_NAME,
                "SecurityCredential": settings.MPESA_SECURITY_CREDENTIAL,
                "CommandID": "TransactionReversal",
                "TransactionID": transaction_id,
                "Amount": str(amount),
                "ReceiverParty": self.business_shortcode,
                "RecieverIdentifierType": "11",
                "ResultURL": f"{settings.PAYMENT_HOST}/api/payment/reversal-callback/",
                "QueueTimeOutURL": f"{settings.PAYMENT_HOST}/api/payment/reversal-timeout/",
                "Remarks": remarks,
                "Occasion": ""
            }
            
            response = requests.post(
                settings.MPESA_REVERSAL_URL,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                'success': result.get('ResponseCode') == "0",
                'message': result.get('ResponseDescription'),
                'refund_id': result.get('RefundRequestID')
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Refund processing error: {str(e)}")
            raise

    def validate_phone_number(self, phone_number):
        """Validate M-Pesa phone number format"""
        # Remove any spaces or special characters
        cleaned = ''.join(filter(str.isdigit, phone_number))
        
        # Check if it's a valid Kenyan phone number
        if not cleaned.startswith('254') or len(cleaned) != 12:
            return False, None
            
        return True, cleaned
