import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { users } from '@/lib/models/user';
import { logSecurityEvent } from '@/lib/utils/logger';

export async function POST(req: Request) {
  try {
    const session = await getServerSession();

    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const user = users.find(u => u.email === session.user.email);

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    if (!user.isTwoFactorEnabled) {
      return NextResponse.json({ error: 'Two-factor authentication is not enabled for this user' }, { status: 400 });
    }

    // Disable 2FA
    user.isTwoFactorEnabled = false;
    user.twoFactorSecret = null;

    logSecurityEvent('DISABLE_2FA', { userId: user.id, email: user.email });

    return NextResponse.json({ message: 'Two-factor authentication has been disabled' });
  } catch (error) {
    console.error('Error in disable 2FA route:', error);
    logSecurityEvent('DISABLE_2FA_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
