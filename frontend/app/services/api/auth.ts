import apiClient from '../api-client';

export interface TwoFactorAuthResponse {
  secret: string;
  qrCodeUrl: string;
}

export interface TwoFactorStatusResponse {
  isEnabled: boolean;
  isVerified: boolean;
}

export interface TwoFactorVerifyResponse {
  success: boolean;
  message?: string;
}

export const twoFactorApi = {
  enable: async (): Promise<TwoFactorAuthResponse> => {
    const response = await apiClient.post('/marketplace/enable-2fa/');
    return response.data;
  },

  verify: async (token: string, secret: string): Promise<TwoFactorVerifyResponse> => {
    const response = await apiClient.post('/marketplace/verify-2fa/', {
      token,
      secret,
    });
    return response.data;
  },

  getStatus: async (): Promise<TwoFactorStatusResponse> => {
    const response = await apiClient.get('/marketplace/2fa-status/');
    return response.data;
  },

  disable: async (): Promise<TwoFactorVerifyResponse> => {
    const response = await apiClient.post('/marketplace/disable-2fa/');
    return response.data;
  },

  validateToken: async (token: string): Promise<TwoFactorVerifyResponse> => {
    const response = await apiClient.post('/marketplace/validate-2fa/', {
      token,
    });
    return response.data;
  },
};

// Add any additional functions or logic as needed
