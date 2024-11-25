import { NextResponse } from 'next/server';
import { users } from '@/lib/models/user';
import { logSecurityEvent } from '@/lib/utils/logger';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const token = searchParams.get('token');

  if (!token) {
    return NextResponse.json({ error: 'Verification token is required' }, { status: 400 });
  }

  const user = users.find(u => u.verificationToken === token);

  if (!user) {
    logSecurityEvent('EMAIL_VERIFICATION_INVALID_TOKEN', { token });
    return NextResponse.json({ error: 'Invalid verification token' }, { status: 400 });
  }

  if (user.isVerified) {
    return NextResponse.json({ message: 'Email already verified' }, { status: 200 });
  }

  // Update user's verification status
  user.isVerified = true;
  user.verificationToken = null;

  logSecurityEvent('EMAIL_VERIFICATION_SUCCESS', { email: user.email });

  return NextResponse.json({ message: 'Email verified successfully' }, { status: 200 });
}
