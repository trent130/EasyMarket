import { NextResponse } from 'next/server';
import { users } from '@/lib/models/user';
import { logSecurityEvent } from '@/lib/utils/logger';
import { hash } from 'bcrypt';
import crypto from 'crypto';

// This is a mock function. In a real application, you would use a proper email service.
async function sendPasswordResetEmail(email: string, token: string) {
  console.log(`Sending password reset email to ${email} with token ${token}`);
  // Simulate email sending delay
  await new Promise(resolve => setTimeout(resolve, 1000));
}

export async function POST(req: Request) {
  try {
    const { email } = await req.json();

    if (!email) {
      return NextResponse.json({ error: 'Email is required' }, { status: 400 });
    }

    const user = users.find(u => u.email === email);

    if (!user) {
      // Don't reveal that the user doesn't exist
      return NextResponse.json({ message: 'If an account exists for this email, a password reset link has been sent.' });
    }

    const resetToken = crypto.randomBytes(20).toString('hex');
    const resetTokenExpiry = Date.now() + 3600000; // 1 hour from now

    // In a real application, you would save the resetToken and resetTokenExpiry to the user's record in the database
    user.resetToken = resetToken;
    user.resetTokenExpiry = resetTokenExpiry;

    await sendPasswordResetEmail(email, resetToken);

    logSecurityEvent('PASSWORD_RESET_REQUESTED', { userId: user.id, email: user.email });

    return NextResponse.json({ message: 'If an account exists for this email, a password reset link has been sent.' });
  } catch (error) {
    console.error('Error in reset password route:', error);
    logSecurityEvent('PASSWORD_RESET_REQUEST_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}

export async function PUT(req: Request) {
  try {
    const { token, newPassword } = await req.json();

    if (!token || !newPassword) {
      return NextResponse.json({ error: 'Token and new password are required' }, { status: 400 });
    }

    const user = users.find(u => u.resetToken === token && u.resetTokenExpiry > Date.now());

    if (!user) {
      return NextResponse.json({ error: 'Invalid or expired reset token' }, { status: 400 });
    }

    const hashedPassword = await hash(newPassword, 10);

    // Update user's password
    user.password = hashedPassword;
    user.resetToken = null;
    user.resetTokenExpiry = null;

    logSecurityEvent('PASSWORD_RESET_SUCCESS', { userId: user.id, email: user.email });

    return NextResponse.json({ message: 'Password has been reset successfully' });
  } catch (error) {
    console.error('Error in reset password route:', error);
    logSecurityEvent('PASSWORD_RESET_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
