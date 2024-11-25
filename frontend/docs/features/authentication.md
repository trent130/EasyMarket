# User Authentication

This document describes the authentication system implemented in our application.

## Features

1. Email and Password Authentication
2. OAuth2 Social Login (Google, GitHub)
3. Multi-factor Authentication (MFA)
4. Password Reset Functionality
5. Account Lockout Protection

## Email and Password Authentication

Users can create an account using their email address and a password. The system implements the following security measures:

- Passwords are hashed using bcrypt before storage
- Password strength is checked using zxcvbn library
- Email verification is required to activate the account

### Registration Process

1. User submits email and password
2. System validates email format and password strength
3. If valid, the password is hashed, and a new user account is created
4. A verification email is sent to the user's email address
5. User clicks the verification link to activate their account

### Login Process

1. User submits email and password
2. System checks if the email exists and if the account is verified
3. If verified, the system compares the submitted password with the stored hash
4. If matched, a session is created for the user

## OAuth2 Social Login

Users can sign in using their Google or GitHub accounts. The process is as follows:

1. User clicks on "Sign in with Google/GitHub" button
2. User is redirected to the respective OAuth provider
3. After successful authentication, the user is redirected back to our application
4. The system creates or updates the user account based on the information provided by the OAuth provider

## Multi-factor Authentication (MFA)

Two types of MFA are supported:

1. Time-based One-Time Password (TOTP)
2. WebAuthn (for supported devices)

Users can enable MFA from their profile settings. Once enabled, they will be required to provide the second factor during login.

## Password Reset Functionality

Users can reset their password if forgotten:

1. User requests a password reset
2. An email with a reset link is sent to the user's email address
3. User clicks the link and is directed to a password reset page
4. User sets a new password

## Account Lockout Protection

To prevent brute-force attacks, the system implements account lockout:

- After a certain number of failed login attempts, the account is temporarily locked
- The lockout duration increases with subsequent failed attempts
- IP-based rate limiting is also implemented to prevent attacks from a single IP address

For more details on the API endpoints related to authentication, please refer to the [API Documentation](../api/README.md).

