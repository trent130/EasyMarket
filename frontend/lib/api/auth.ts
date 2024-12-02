import apiClient  from '../api-client';

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
    const response = await apiClient.post('/auth/enable-2fa/');
    return response.data;
  },

  verify: async (token: string, secret: string): Promise<TwoFactorVerifyResponse> => {
    const response = await apiClient.post('/auth/verify-2fa/', {
      token,
      secret,
    });
    return response.data;
  },

  getStatus: async (): Promise<TwoFactorStatusResponse> => {
    const response = await apiClient.get('/auth/2fa-status/');
    return response.data;
  },

  disable: async (): Promise<TwoFactorVerifyResponse> => {
    const response = await apiClient.post('/auth/disable-2fa/');
    return response.data;
  },

  validateToken: async (token: string): Promise<TwoFactorVerifyResponse> => {
    const response = await apiClient.post('/auth/validate-2fa/', {
      token,
    });
    return response.data;
  },
};
