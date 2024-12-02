import { authenticator } from 'otplib';
import QRCode from 'qrcode';

export const generateSecret = () => {
  return authenticator.generateSecret();
};

export const generateQRCode = async (secret: string, email: string) => {
  const service = 'EasyMarket';
  const otpauth = authenticator.keyuri(email, service, secret);
  return await QRCode.toDataURL(otpauth);
};

export const verifyToken = (token: string, secret: string) => {
  return authenticator.verify({ token, secret });
};

// Function to verify 2FA with Django backend
export const verify2FAWithBackend = async (userId: string, token: string, secret: string) => {
  try {
    const response = await fetch('http://localhost:8000/api/auth/verify-2fa/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        token,
        secret,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to verify 2FA');
    }

    const data = await response.json();
    return data.verified;
  } catch (error) {
    console.error('Error verifying 2FA:', error);
    throw error;
  }
};

// Function to enable 2FA with Django backend
export const enable2FAWithBackend = async (userId: string) => {
  try {
    const response = await fetch('http://localhost:8000/api/auth/enable-2fa/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to enable 2FA');
    }

    const data = await response.json();
    return {
      secret: data.secret,
      qrCodeUrl: data.qr_code_url,
    };
  } catch (error) {
    console.error('Error enabling 2FA:', error);
    throw error;
  }
};
