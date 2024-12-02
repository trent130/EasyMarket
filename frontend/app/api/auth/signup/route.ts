import { NextResponse } from 'next/server';
import { hash } from 'bcrypt';
import crypto from 'crypto';
import { users } from '@/lib/models/user';
import { logSecurityEvent } from '@/lib/utils/logger';

// This is a mock function. In a real application, you would use a proper email service.
async function sendVerificationEmail(email: string, token: string) {
  console.log(`Sending verification email to ${email} with token ${token}`);
  // Simulate email sending delay
  await new Promise(resolve => setTimeout(resolve, 1000));
}

async function verifyCaptcha(token: string) {
  const secretKey = process.env.RECAPTCHA_SECRET_KEY;
  const verifyUrl = `https://www.google.com/recaptcha/api/siteverify?secret=${secretKey}&response=${token}`;

  const response = await fetch(verifyUrl, { method: 'POST' });
  const data = await response.json();
  return data.success;
}

export async function POST(req: Request) {
  try {
    const { name, email, password, captchaToken } = await req.json();

    // Basic validation
    if (!name || !email || !password || !captchaToken) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    // Verify CAPTCHA
    const isCaptchaValid = await verifyCaptcha(captchaToken);
    if (!isCaptchaValid) {
      logSecurityEvent('SIGNUP_INVALID_CAPTCHA', { email });
      return NextResponse.json({ error: 'Invalid CAPTCHA' }, { status: 400 });
    }

    // Check if user already exists
    if (users.find(user => user.email === email)) {
      return NextResponse.json({ error: 'User already exists' }, { status: 409 });
    }

    // Hash the password
    const hashedPassword = await hash(password, 10);

    // Generate verification token
    const verificationToken = crypto.randomBytes(20).toString('hex');

    // Create new user
    const newUser = {
      id: (users.length + 1).toString(),
      name,
      email,
      password: hashedPassword,
      isVerified: false,
      verificationToken
    };

    // Add user to mock database
    users.push(newUser);

    // Send verification email
    await sendVerificationEmail(email, verificationToken);

    logSecurityEvent('USER_SIGNUP', { email });

    return NextResponse.json({ message: 'User created successfully. Please check your email to verify your account.' }, { status: 201 });
  } catch (error) {
    console.error('Error in signup route:', error);
    logSecurityEvent('USER_SIGNUP_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
