import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/marketplace';

export interface TwoFactorAuthResponse {
  secret: string;
  qrCodeUrl: string;
}

export interface TwoFactorStatusResponse {
  isEnabled: boolean;
  isVerified: boolean;
}


export interface SignInResponse {
  message: string;
  token: string; // Assuming a token is returned on successful sign-in
}

export interface SignUpResponse {
  message: string;
}

export interface ForgotPasswordResponse {
  message: string;
}

export interface TwoFactorVerifyResponse {
  success: boolean;
  message?: string;
}

class AuthService {
  /**
   * Returns an object containing the Authorization header with a Bearer token
   * if the token exists in local storage, otherwise returns an empty object.
   * @returns {{ Authorization: string } | {}}
   * @private
   */
  private getAuthHeader() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  /**
   * Enables two-factor authentication for the current user.
   * @returns A promise that resolves to an object containing the secret key and QR code URL.
   * @throws An error if the request fails.
   */
  async enable2FA(): Promise<TwoFactorAuthResponse> {
    const response = await axios.post(
      `${API_URL}/auth/enable-2fa/`,
      {},
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  /**
   * Verifies the provided two-factor authentication (2FA) token with the given secret.
   *
   * @param token - The 2FA token to be verified.
   * @param secret - The secret used to validate the 2FA token.
   * @returns A promise that resolves to a TwoFactorVerifyResponse containing the verification result.
   * @throws An error if the request fails.
   */
  async verify2FA(token: string, secret: string): Promise<TwoFactorVerifyResponse> {
    const response = await axios.post(
      `${API_URL}/auth/verify-2fa/`,
      { token, secret },
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  /**
   * Retrieves the two-factor authentication status of the current user.
   * @returns An object containing a boolean indicating whether 2FA is enabled and a boolean indicating whether 2FA has been verified for the current user.
   */
  async get2FAStatus(): Promise<TwoFactorStatusResponse> {
    const response = await axios.get(
      `${API_URL}/auth/2fa-status/`,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  /**
   * Disables two-factor authentication for the current user.
   * @returns An object indicating success or failure of the operation
   */
  async disable2FA(): Promise<TwoFactorVerifyResponse> {
    const response = await axios.post(
      `${API_URL}/auth/disable-2fa/`,
      {},
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  /**
   * Validates a two-factor authentication (2FA) token.
   *
   * @param token - The 2FA token to be validated.
   * @returns A promise that resolves to a TwoFactorVerifyResponse containing the validation result.
   * @throws An error if the request fails.
   */
  async validate2FAToken(token: string): Promise<TwoFactorVerifyResponse> {
    const response = await axios.post(
      `${API_URL}/auth/validate-2fa/`,
      { token },
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

/**
 * Refreshes the access token using the provided refresh token.
 *
 * @param refreshToken - The refresh token used to obtain a new access token.
 * @returns A promise that resolves to an object containing the new access token.
 */
  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    const response = await axios.post(`${API_URL}/token/refresh/`, {
      refresh: refreshToken,
    });
    return response.data;
  }

/**
 * Authenticates a user using their username and password.
 *
 * @param username - The username of the user attempting to sign in.
 * @param password - The password of the user attempting to sign in.
 * @returns A Promise that resolves to a SignInResponse containing a message and token if successful.
 */
  async signIn(username: string, password: string): Promise<SignInResponse> {
    const response = await axios.post(`${API_URL}/auth/signin/`, {
        username,
        password,
    });
    return response.data;
  }

/**
 * Registers a new user with the provided username, email, and password.
 *
 * @param username - The username for the new account.
 * @param email - The email address associated with the new account.
 * @param password - The password for the new account.
 * @returns A Promise that resolves to a SignUpResponse containing a message.
 */
  async signUp(username: string, email: string, password: string): Promise<SignUpResponse> {
    const response = await axios.post(`${API_URL}/auth/signup/`, {
        username,
        email,
        password,
    });
    return response.data;
  }

  /**
   * Sends an email with a link to reset the user's password.
   *
   * @param email - The email address associated with the account to reset the password for.
   * @returns A Promise that resolves to a ForgotPasswordResponse containing a message.
   */
  async forgotPassword(email: string): Promise<ForgotPasswordResponse> {
    const response = await axios.post(`${API_URL}/auth/forgot-password/`, {
        email,
    });
    return response.data;
  }

}

export const authService = new AuthService();
export default authService;
