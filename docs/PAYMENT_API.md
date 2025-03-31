# Payment API Documentation

## M-Pesa Integration

### Configuration
```python
# settings.py
MPESA_ENVIRONMENT = 'sandbox'  # or 'production'
MPESA_CONSUMER_KEY = 'your_consumer_key'
MPESA_CONSUMER_SECRET = 'your_consumer_secret'
MPESA_SHORTCODE = 'your_shortcode'
MPESA_PASSKEY = 'your_passkey'
```

### Endpoints

#### 1. Initiate Payment
```http
POST /api/payment/mpesa/
Content-Type: application/json
Authorization: Bearer <token>

{
    "phone_number": "254712345678",
    "order_id": 123,
    "amount": 1000.00
}
```

Response:
```json
{
    "message": "Payment initiated",
    "transaction_id": "TXN20230815123456ABC",
    "checkout_request_id": "ws_CO_123456789"
}
```

#### 2. Verify Payment
```http
POST /api/payment/verify/
Content-Type: application/json
Authorization: Bearer <token>

{
    "transaction_id": "TXN20230815123456ABC",
    "order_id": 123
}
```

Response:
```json
{
    "status": "completed",
    "message": "Payment successful"
}
```

### Callback URLs

#### M-Pesa STK Push Callback
```http
POST /api/payment/mpesa-callback/
Content-Type: application/json

{
    "Body": {
        "stkCallback": {
            "MerchantRequestID": "123",
            "CheckoutRequestID": "ws_CO_123456789",
            "ResultCode": 0,
            "ResultDesc": "The service request is processed successfully."
        }
    }
}
```

## Transaction Management

### 1. Get Transaction History
```http
GET /api/payment/history/
Authorization: Bearer <token>
```

Response:
```json
{
    "results": [
        {
            "id": "TXN20230815123456ABC",
            "amount": 1000.00,
            "status": "completed",
            "payment_method": "mpesa",
            "created_at": "2023-08-15T12:34:56Z"
        }
    ],
    "total": 1,
    "page": 1
}
```

### 2. Get Transaction Receipt
```http
GET /api/payment/transactions/{transaction_id}/receipt/
Authorization: Bearer <token>
```

Response:
```json
{
    "receipt_number": "RCP20230815123456ABC",
    "date": "2023-08-15 12:34:56",
    "amount": "KES 1,000.00",
    "payment_method": "M-Pesa",
    "status": "Completed",
    "customer_name": "John Doe",
    "order_reference": "Order #123"
}
```

### 3. Request Refund
```http
POST /api/payment/transactions/{transaction_id}/refund/
Content-Type: application/json
Authorization: Bearer <token>

{
    "amount": 1000.00,
    "reason": "Customer request"
}
```

Response:
```json
{
    "message": "Refund processed successfully",
    "refund_id": "RFD20230815123456ABC"
}
```

## Payment Methods

### 1. List Payment Methods
```http
GET /api/payment/methods/
Authorization: Bearer <token>
```

Response:
```json
{
    "methods": [
        {
            "type": "mpesa",
            "display_name": "M-Pesa",
            "enabled": true,
            "currency": "KES"
        }
    ]
}
```

### 2. Add Payment Method
```http
POST /api/payment/methods/
Content-Type: application/json
Authorization: Bearer <token>

{
    "type": "mpesa",
    "details": {
        "phone_number": "254712345678"
    },
    "is_default": true
}
```

## Error Handling

### Error Response Format
```json
{
    "error": "Error message",
    "code": "ERROR_CODE",
    "details": {}
}
```

### Common Error Codes
- `INVALID_PHONE`: Invalid phone number format
- `AMOUNT_TOO_LOW`: Amount below minimum allowed
- `AMOUNT_TOO_HIGH`: Amount exceeds maximum allowed
- `PAYMENT_FAILED`: Payment processing failed
- `PAYMENT_EXPIRED`: Payment request expired
- `INVALID_CURRENCY`: Invalid currency for payment method

## WebSocket Events

### Payment Status Updates
```javascript
// Subscribe to payment updates
ws.subscribe(WebSocketMessageType.PAYMENT_UPDATE, (data) => {
    console.log('Payment status:', data.status);
});
```

## Testing

### Test Payment (Sandbox)
```http
POST /api/payment/test/mpesa/
Content-Type: application/json
Authorization: Bearer <token>

{
    "phone_number": "254712345678",
    "amount": 1000.00
}
```

### Test Callback
```http
POST /api/payment/test/callback/
Content-Type: application/json

{
    "transaction_id": "TXN20230815123456ABC",
    "status": "completed"
}
```

## Security

### Authentication
All API endpoints require authentication using JWT tokens:
```http
Authorization: Bearer <token>
```

### Rate Limiting
- 100 requests per minute for payment initiation
- 1000 requests per minute for payment status checks

### Data Validation
- Phone numbers must be in format: 254XXXXXXXXX
- Amount must be within method limits
- Currency must match payment method

## Integration Steps

1. Configure M-Pesa credentials in settings
2. Implement payment initiation in checkout flow
3. Handle callback notifications
4. Implement payment verification
5. Add error handling and retry logic
6. Test thoroughly in sandbox environment
7. Monitor transactions and handle support cases

## Best Practices

1. Always verify payment status before fulfilling orders
2. Implement idempotency for payment requests
3. Store transaction logs for reconciliation
4. Handle timeout and network errors gracefully
5. Implement proper security measures
6. Monitor payment success rates
7. Keep payment credentials secure
