# Authentication Flow Diagram

This diagram illustrates the basic flow of the authentication process in our system.

```mermaid
sequenceDiagram
    participant User
    participant Client
    participant AuthServer
    participant ResourceServer
    participant Database

    User->>Client: Enter Credentials
    Client->>AuthServer: Send Credentials
    AuthServer->>Database: Validate Credentials
    Database-->>AuthServer: Credentials Valid
    AuthServer->>AuthServer: Generate Tokens
    AuthServer-->>Client: Return Access & Refresh Tokens
    Client->>ResourceServer: Request Resource with Access Token
    ResourceServer->>AuthServer: Validate Token
    AuthServer-->>ResourceServer: Token Valid
    ResourceServer-->>Client: Return Requested Resource
    Client-->>User: Display Resource

    Note over User,Database: If 2FA is enabled
    AuthServer->>User: Request 2FA Code
    User->>AuthServer: Provide 2FA Code
    AuthServer->>AuthServer: Validate 2FA Code

    Note over User,Database: OAuth Flow
    User->>Client: Request OAuth Login
    Client->>AuthServer: Redirect to OAuth Provider
    AuthServer->>User: Request Authorization
    User->>AuthServer: Grant Authorization
    AuthServer-->>Client: Return Authorization Code
    Client->>AuthServer: Exchange Code for Tokens
    AuthServer-->>Client: Return Access & Refresh Tokens
```

This diagram shows the following key steps:

1. User enters credentials in the client application.
2. Client sends credentials to the authentication server.
3. Auth server validates credentials against the database.
4. If valid, auth server generates access and refresh tokens.
5. Client receives tokens and uses the access token to request resources.
6. Resource server validates the token with the auth server before serving the resource.
7. If 2FA is enabled, there's an additional step for 2FA code validation.
8. For OAuth flow, there are additional steps involving user authorization and code exchange.

Note: This is a simplified representation. Actual implementation may involve additional steps and security measures.
