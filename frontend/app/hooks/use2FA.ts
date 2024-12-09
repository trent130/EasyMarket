import { useState } from 'react';
import { useSession } from 'next-auth/react';
// import { enable2FAWithBackend, verify2FAWithBackend } from '../utils/twoFactorAuth';

export function use2FA() {
  const { data: session } = useSession();
  const [isEnabling, setIsEnabling] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [qrCode, setQrCode] = useState<string | null>(null);
  const [secret, setSecret] = useState<string | null>(null);

  const enable2FA = async () => {
    if (!session?.user) {
      setError('You must be logged in to enable 2FA');
      return;
    }

    setIsEnabling(true);
    setError(null);

    try {
      const response = await fetch('/marketplace/enable-2fa', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to enable 2FA');
      }

      setQrCode(data.qrCodeUrl);
      setSecret(data.secret);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsEnabling(false);
    }
  };

  const verify2FA = async (token: string) => {
    if (!session?.user || !secret) {
      setError('Invalid state for 2FA verification');
      return false;
    }

    setIsVerifying(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/verify-2fa', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token, secret }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to verify 2FA');
      }

      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      return false;
    } finally {
      setIsVerifying(false);
    }
  };

  return {
    enable2FA,
    verify2FA,
    isEnabling,
    isVerifying,
    error,
    qrCode,
    secret,
  };
}
