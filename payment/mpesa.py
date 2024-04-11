import requests
import base64
import datetime

class MpesaClient:
    def __init__(self, api_key, api_secret, shortcode, environment):
        self.api_key = api_key
        self.api_secret = api_secret
        self.shortcode = shortcode
        self.environment = environment
        self.generate_access_token()
        self.generate_password()
        self.generate_timestamp()
        self.generate_account_reference()
        
    def stk_push(self, phone_number, amount, account_reference, transaction_desc, callback_url):
        # Make a POST request to initiate STK push payment
        url = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        headers = {
            'Authorization': f'Bearer {self.generate_access_token()}',
            'Content-Type': 'application/json'
        }
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': self.generate_password(),
            'Timestamp': self.generate_timestamp(),
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': amount,
            'PartyA': phone_number,
            'PartyB': self.shortcode,
            'PhoneNumber': phone_number,
            'CallBackURL': callback_url,
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()  # Return the response JSON

    def generate_access_token(self):
        credentials = f"{self.api_key}:{self.api_secret}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        headers = {
            'Authorization': f'Basic {encoded_credentials}'
        }
        url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            # Handle error appropriately
            return None


    def generate_password(self):
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        raw_password = f"{self.shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(raw_password.encode('utf-8')).decode('utf-8')



    def generate_timestamp(self):
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S')