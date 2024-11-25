"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import ReCAPTCHA from "react-google-recaptcha";
import { checkPasswordStrength, PasswordStrengthResult } from '@/lib/utils/passwordStrength';

export default function SignUp() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [passwordStrength, setPasswordStrength] = useState<PasswordStrengthResult | null>(null);
  const router = useRouter();
  const recaptchaRef = React.useRef<ReCAPTCHA>(null);

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPassword = e.target.value;
    setPassword(newPassword);
    setPasswordStrength(checkPasswordStrength(newPassword));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!name || !email || !password || !confirmPassword) {
      setError('Please fill in all fields');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (!passwordStrength || passwordStrength.score < 3) {
      setError('Please choose a stronger password');
      return;
    }

    const captchaToken = recaptchaRef.current?.getValue();
    if (!captchaToken) {
      setError('Please complete the CAPTCHA');
      return;
    }

    try {
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password, captchaToken }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(data.message);
        setTimeout(() => router.push('/auth/signin'), 3000);
      } else {
        setError(data.error || 'An error occurred during signup');
      }
    } catch (error) {
      setError('An error occurred. Please try again.');
    } finally {
      recaptchaRef.current?.reset();
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <div className="w-full max-w-md space-y-8 rounded-xl bg-white p-10 shadow-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">Create your account</h2>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {/* ... (keep existing form fields) ... */}
          <div>
            <label htmlFor="password" className="sr-only">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="new-password"
              required
              className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Password"
              value={password}
              onChange={handlePasswordChange}
            />
          </div>
          {passwordStrength && (
            <div className="text-sm">
              <p className={`font-semibold ${
                passwordStrength.score < 3 ? 'text-red-500' : 'text-green-500'
              }`}>
                Password strength: {['Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'][passwordStrength.score]}
              </p>
              {passwordStrength.feedback.warning && (
                <p className="text-yellow-500">{passwordStrength.feedback.warning}</p>
              )}
              {passwordStrength.feedback.suggestions.map((suggestion, index) => (
                <p key={index} className="text-gray-600">{suggestion}</p>
              ))}
            </div>
          )}
          {/* ... (keep the rest of the form) ... */}
        </form>
      </div>
    </div>
  );
}
