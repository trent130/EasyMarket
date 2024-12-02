import { NextResponse } from 'next/server';
import { rateLimit } from '@/lib/utils/rateLimiter';

// This is a mock function. In a real application, you would use a proper email service.
async function sendPasswordResetEmail(email: string, resetToken: string) {
  console.log(`Sending password reset email to ${email} with token ${resetToken}`);
  // Simulate email sending delay
  await new Promise(resolve => setTimeout(resolve, 1000));
}

export async function POST(req: Request) {
  try {
    const { email } = await req.json();

    if (!email) {
      return NextResponse.json({ error: 'Email is required' }, { status: 400 });
    }

    if (!rateLimit(email)) {
      return NextResponse.json({ error: 'Too many requests. Please try again later.' }, { status: 429 });
    }

    // In a real application, you would:
    // 1. Check if the user exists in your database
    // 2. Generate a unique reset token
    // 3. Save the token in the database with an expiration time
    // 4. Send an email to the user with a link containing the token

    // For this example, we'll simulate the process
    const resetToken = Math.random().toString(36).substring(2, 15);

    await sendPasswordResetEmail(email, resetToken);

    return NextResponse.json({ message: 'If an account exists for this email, a password reset link has been sent.' });
  } catch (error) {
    console.error('Error in forgot password route:', error);
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
