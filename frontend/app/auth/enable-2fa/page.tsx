"use client";

import { useState } from 'react';
import Image from 'next/image';

export default function Enable2FA() {
  const [qrCode, setQrCode] = useState<string | null>(null);
  const [secret, setSecret] = useState<string | null>(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleEnable2FA = async () => {
    try {
      // In a real application, you would get the user ID from the session
      const userId = '1'; // Hardcoded for this example
      const response = await fetch('/api/auth/enable-2fa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId }),
      });

      const data = await response.json();

      if (response.ok) {
        setQrCode(data.qrCodeUrl);
        setSecret(data.secret);
      } else {
        setError(data.error || 'An error occurred');
      }
    } catch (error) {
      setError('An error occurred');
    }
  };

  const handleVerify = async () => {
    try {
      // In a real application, you would send this to your backend for verification
      const response = await fetch('/api/auth/verify-2fa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId: '1', token: verificationCode, secret }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('Two-factor authentication enabled successfully');
      } else {
        setError(data.error || 'Verification failed');
      }
    } catch (error) {
      setError('An error occurred');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <div className="w-full max-w-md space-y-8 rounded-xl bg-white p-10 shadow-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">Enable Two-Factor Authentication</h2>
        {!qrCode ? (
          <button
            onClick={handleEnable2FA}
            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Enable 2FA
          </button>
        ) : (
          <div className="space-y-4">
            <div className="flex justify-center">
              <Image src={qrCode} alt="QR Code" width={200} height={200} />
            </div>
            <p className="text-center text-sm">Scan this QR code with your authenticator app</p>
            <input
              type="text"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value)}
              placeholder="Enter verification code"
              className="appearance-none rounded relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
            <button
              onClick={handleVerify}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Verify and Enable
            </button>
          </div>
        )}
        {error && <p className="mt-2 text-center text-sm text-red-600">{error}</p>}
        {success && <p className="mt-2 text-center text-sm text-green-600">{success}</p>}
      </div>
    </div>
  );
}
