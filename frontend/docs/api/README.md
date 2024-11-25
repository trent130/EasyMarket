# API Documentation

This document provides an overview of the API endpoints available in our application. For detailed information about each endpoint, including request/response formats and authentication requirements, please refer to the specific documentation files.

## Authentication

All API requests (except for login and registration) require authentication. Use the following header:

```
Authorization: Bearer <access_token>
```

## Base URL

All API requests should be prefixed with:

```
https://api.example.com/v1
```

## Endpoints

### User Authentication

- POST /auth/register - Register a new user
- POST /auth/login - Authenticate a user and receive an access token
- POST /auth/logout - Invalidate the current access token
- POST /auth/refresh - Refresh an access token
- POST /auth/forgot-password - Initiate the password reset process
- POST /auth/reset-password - Reset the password using a token

### User Profile

- GET /user/profile - Retrieve the current user's profile
- PUT /user/profile - Update the current user's profile
- PUT /user/password - Change the current user's password

### Two-Factor Authentication

- POST /auth/2fa/enable - Enable 2FA for the current user
- POST /auth/2fa/disable - Disable 2FA for the current user
- POST /auth/2fa/verify - Verify a 2FA code during login
- GET /auth/2fa/backup-codes - Generate new backup codes

### WebAuthn

- POST /auth/webauthn/register/options - Get options for WebAuthn registration
- POST /auth/webauthn/register/verify - Verify WebAuthn registration
- POST /auth/webauthn/authenticate/options - Get options for WebAuthn authentication
- POST /auth/webauthn/authenticate/verify - Verify WebAuthn authentication

### Data Export

- POST /user/data-export - Request a data export
- GET /user/data-export/{exportId} - Check the status of a data export
- GET /user/data-export/{exportId}/download - Download the exported data

### Third-Party Apps

- GET /user/authorized-apps - List all authorized third-party apps
- DELETE /user/authorized-apps/{appId} - Revoke access for a specific app
- POST /oauth/authorize - Authorize a new third-party app
- POST /oauth/token - Exchange an authorization code for an access token

### Account Management

- POST /user/delete-account - Initiate account deletion process

## Error Handling

All endpoints use standard HTTP status codes. In case of an error, the response will include a JSON object with an `error` field describing the issue.

Example error response:

```json
{
  "error": "Invalid credentials"
}
```

## Rate Limiting

API requests are subject to rate limiting. The current limits are:

- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated requests

When the rate limit is exceeded, the API will respond with a 429 (Too Many Requests) status code.

## Versioning

The API version is included in the URL (e.g., `/v1/`). When we make backwards-incompatible changes to the API, we will release a new version number.

