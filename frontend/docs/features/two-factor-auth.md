# Two-Factor Authentication (2FA)

This document describes the two-factor authentication (2FA) system implemented in our application.

## Supported 2FA Methods

1. Time-based One-Time Password (TOTP)
2. WebAuthn (for supported devices)

## TOTP Implementation

Time-based One-Time Password (TOTP) is an algorithm that generates a one-time password which uses the current time as a source of uniqueness.

### Setup Process

1. User navigates to 2FA settings in their profile
2. User chooses to enable TOTP
3. System generates a secret key
4. System displays a QR code and the secret key to the user
5. User scans the QR code with their authenticator app (e.g., Google Authenticator, Authy)
6. User enters the current TOTP code to verify setup
7. System validates the code and enables TOTP for the user's account

### Authentication Process

1. User enters their username and password
2. If correct, the system prompts for the TOTP code
3. User enters the current code from their authenticator app
4. System validates the code
5. If valid, the user is granted access

## WebAuthn Implementation

WebAuthn (Web Authentication) is a web standard published by the World Wide Web Consortium (W3C). It allows servers to register and authenticate users using public key cryptography instead of a password.

### Setup Process

1. User navigates to 2FA settings in their profile
2. User chooses to enable WebAuthn
3. System initiates the WebAuthn registration process
4. User's browser prompts them to create a new credential (e.g., using a security key or biometric)
5. User completes the credential creation process
6. Browser sends the credential public key and other registration data to the server
7. Server validates and stores the credential information

### Authentication Process

1. User enters their username
2. System initiates the WebAuthn authentication process
3. User's browser prompts them to use their WebAuthn method (e.g., touch their security key or use biometric)
4. User completes the authentication
5. Browser sends the authentication data to the server
6. Server validates the authentication and grants access if valid

## Backup Codes

To ensure users don't lose access to their accounts, we provide backup codes when 2FA is enabled.

1. System generates a set of one-time use backup codes
2. User is prompted to save these codes securely
3. If a user loses access to their 2FA method, they can use a backup code to gain access
4. Once a backup code is used, it becomes invalid

## Security Considerations

- TOTP secrets and WebAuthn credential information are stored securely and encrypted
- Failed 2FA attempts are logged and count towards account lockout thresholds
- Users are notified via email when 2FA is enabled, disabled, or when backup codes are used
- 2FA can be required for sensitive operations (e.g., changing password, disabling 2FA)

## Disabling 2FA

1. User navigates to 2FA settings in their profile
2. User chooses to disable 2FA
3. System requires re-authentication and possibly additional verification
4. If verified, 2FA is disabled for the account

For more details on the API endpoints related to two-factor authentication, please refer to the [API Documentation](../api/README.md).

