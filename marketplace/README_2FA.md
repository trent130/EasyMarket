# Two-Factor Authentication Implementation

## Setup Instructions

1. Install required dependencies:
```bash
pip install -r requirements_2fa.txt
```

2. Apply migrations:
```bash
python manage.py migrate marketplace
```

3. Update Django settings:
Add 'marketplace.middleware.TwoFactorMiddleware' to MIDDLEWARE in settings.py.

## API Endpoints

### Enable 2FA
- URL: `/api/auth/enable-2fa/`
- Method: POST
- Authentication: Required
- Response: Returns secret key and QR code URL

### Verify 2FA
- URL: `/api/auth/verify-2fa/`
- Method: POST
- Authentication: Required
- Body: 
  ```json
  {
    "token": "123456",
    "secret": "your_secret"
  }
  ```

### Get 2FA Status
- URL: `/api/auth/2fa-status/`
- Method: GET
- Authentication: Required
- Response: Returns enabled/verified status

### Disable 2FA
- URL: `/api/auth/disable-2fa/`
- Method: POST
- Authentication: Required
- Body:
  ```json
  {
    "token": "123456"
  }
  ```

### Validate Backup Code
- URL: `/api/auth/validate-backup-code/`
- Method: POST
- Authentication: Required
- Body:
  ```json
  {
    "code": "ABCD1234"
  }
  ```

### Regenerate Backup Codes
- URL: `/api/auth/regenerate-backup-codes/`
- Method: POST
- Authentication: Required

## Protected Routes

The following routes require 2FA verification when enabled:
- /api/orders/
- /api/payment/
- /api/profile/
- /api/settings/

## Integration with Frontend

The frontend should:
1. Check 2FA status on login
2. Prompt for 2FA setup if not enabled
3. Request 2FA verification for protected routes
4. Handle backup codes for account recovery

## Security Considerations

1. Tokens are time-based (TOTP) and valid for 30 seconds
2. Backup codes are single-use
3. Secret keys are stored encrypted
4. Failed attempts are rate-limited
5. Protected routes enforce 2FA verification

## Testing

Test cases should cover:
1. Enable/disable flow
2. Token verification
3. Backup code usage
4. Protected route access
5. Error handling

## Troubleshooting

Common issues:
1. Token verification fails: Check time synchronization
2. QR code doesn't scan: Verify proper encoding
3. Protected routes not enforced: Check middleware configuration
