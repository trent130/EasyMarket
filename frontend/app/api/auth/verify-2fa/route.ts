import { NextResponse } from 'next/server';
import { verifyTOTP } from '@/lib/utils/twoFactorAuth';
import { users } from '@/lib/models/user';

export async function POST(req: Request) {
  try {
    const { userId, token, secret } = await req.json();

    if (!userId || !token || !secret) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    const user = users.find(u => u.id === userId);

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    if (user.isTwoFactorEnabled) {
      return NextResponse.json({ error: 'Two-factor authentication is already enabled' }, { status: 400 });
    }

    const isValid = verifyTOTP(token, secret);

    if (!isValid) {
      return NextResponse.json({ error: 'Invalid verification code' }, { status: 400 });
    }

    // In a real application, you would update the user's record in the database
    user.isTwoFactorEnabled = true;
    user.twoFactorSecret = secret;

    return NextResponse.json({ message: 'Two-factor authentication enabled successfully' });
  } catch (error) {
    console.error('Error in verify 2FA route:', error);
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
