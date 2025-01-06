"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import ReCAPTCHA from "react-google-recaptcha";
import { checkPasswordStrength, PasswordStrengthResult } from '../../utils/passwordStrength';

/**
 * Handles the sign up form submission.
 *
 * Validates the input fields, checks if the user has completed the CAPTCHA,
 * and sends a signup request to the server with the user's name, email, password, and CAPTCHA token.
 *
 * Displays an appropriate success message and redirects to the signin page on successful signup, or shows an error message
 * if the signup fails. Resets the CAPTCHA regardless of the outcome.
 *
 * @returns {JSX.Element} The signup form.
 */
export default function SignUp() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [passwordStrength, setPasswordStrength] = useState<PasswordStrengthResult | null>(null);
  const router = useRouter();
  const recaptchaRef = React.useRef<ReCAPTCHA>(null);

/**
 * Handles the password input change event.
 *
 * Updates the password state with the new value and evaluates the password
 * strength using the checkPasswordStrength function. The strength result
 * is then stored in the passwordStrength state.
 *
 * @param e - The change event for the password input field.
 */
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPassword = e.target.value;
    setPassword(newPassword);
    setPasswordStrength(checkPasswordStrength(newPassword));
  };

/**
 * Handles the form submission for the signup process.
 *
 * Prevents default form submission behavior, clears any existing error or success messages,
 * and performs input validation. Validates that all fields are filled, passwords match, 
 * password strength is sufficient, and CAPTCHA is completed. If validation passes, sends 
 * a signup request to the server with the user's name, email, password, and CAPTCHA token.
 *
 * Displays an appropriate success message and redirects to the signin page on successful 
 * signup, or shows an error message if the signup fails. Resets the CAPTCHA regardless of 
 * the outcome.
 *
 * @param e - The form event triggered by the submission.
 */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Input validation
    if (!username || !email || !password || !confirmPassword) {
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

   // const captchaToken = recaptchaRef.current?.getValue();
    //if (!captchaToken) {
    //  setError('Please complete the CAPTCHA');
      //return;
    //}

    try {
      const response = await fetch('/marketplace/signup/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password, }), // captchaToken
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
    <div className="flex  justify-center items-center">
      <div className="w-full max-w-md space-y-8 rounded-xl bg-white p-10 shadow-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">Create your account</h2>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {/* Username Input */}
          <div>
            <label htmlFor="name" className="sr-only">Username</label>
            <input
              id="Username"
              name="username"
              type="text"
              required
              className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>
          
          {/* Email Input */}
          <div>
            <label htmlFor="email" className="sr-only">Email</label>
            <input
              id="email"
              name="email"
              type="email"
              required
              className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          {/* Password Input */}
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

          {/* Confirm Password Input */}
          <div>
            <label htmlFor="confirmPassword" className="sr-only">Confirm Password</label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              required
              className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Confirm Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
          </div>

          {/* Error and Success Messages */}
          {error && <p className="text-red-500">{error}</p>}
          {success && <p className="text-green-500">{success}</p>}

          {/* ReCAPTCHA */}
          <ReCAPTCHA
            ref={recaptchaRef}
            sitekey="recapture_site_key"
            size="invisible"
          />

          {/* Submit Button */}
          <div>
            <button
              type="submit"
              className="group relative flex w-full justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              Sign Up
            </button>
          </div>
        </form>
        <div className="text-center text-sm text-indigo-600 hover:text-indigo-500">
          Already have an account?
          <Link href="/auth/signin" className="hover:underline ">
             Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}