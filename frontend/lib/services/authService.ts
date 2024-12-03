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
  private getAuthHeader() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async enable2FA(): Promise<TwoFactorAuthResponse> {
    const response = await axios.post(
      `${API_URL}/auth/enable-2fa/`,
      {},
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async verify2FA(token: string, secret: string): Promise<TwoFactorVerifyResponse> {
    const response = await axios.post(
      `${API_URL}/auth/verify-2fa/`,
      { token, secret },
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async get2FAStatus(): Promise<TwoFactorStatusResponse> {
    const response = await axios.get(
      `${API_URL}/auth/2fa-status/`,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async disable2FA(): Promise<TwoFactorVerifyResponse> {
    const response = await axios.post(
      `${API_URL}/auth/disable-2fa/`,
      {},
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async validate2FAToken(token: string): Promise<TwoFactorVerifyResponse> {
    const response = await axios.post(
      `${API_URL}/auth/validate-2fa/`,
      { token },
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    const response = await axios.post(`${API_URL}/token/refresh/`, {
      refresh: refreshToken,
    });
    return response.data;
  }

  async signIn(username: string, password: string): Promise<SignInResponse> {
    const response = await axios.post(`${API_URL}/auth/signin/`, {
        username,
        password,
    });
    return response.data;
  }

  async signUp(username: string, email: string, password: string): Promise<SignUpResponse> {
    const response = await axios.post(`${API_URL}/auth/signup/`, {
        username,
        email,
        password,
    });
    return response.data;
  }

  async forgotPassword(email: string): Promise<ForgotPasswordResponse> {
    const response = await axios.post(`${API_URL}/auth/forgot-password/`, {
        email,
    });
    return response.data;
  }

}

export const authService = new AuthService();
export default authService;
