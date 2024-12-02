import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { users } from '@/lib/models/user';
import { logSecurityEvent } from '@/lib/utils/logger';
import { generateAndSendEmailCode } from '@/lib/utils/emailAuth';

const EMAIL_CODE_EXPIRY = 10 * 60 * 1000; // 10 minutes

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

    const code = await generateAndSendEmailCode(user.email);
    
    // In a real application, you would store this securely, possibly encrypted
    user.emailAuthCode = code;
    user.emailAuthCodeExpiry = Date.now() + EMAIL_CODE_EXPIRY;

    logSecurityEvent('EMAIL_2FA_CODE_SENT', { userId: user.id, email: user.email });

    return NextResponse.json({ message: 'Email authentication code sent' });
  } catch (error) {
    console.error('Error in email 2FA route:', error);
    logSecurityEvent('EMAIL_2FA_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}

export async function PUT(req: Request) {
  try {
    const session = await getServerSession();

    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { code } = await req.json();

    if (!code) {
      return NextResponse.json({ error: 'Authentication code is required' }, { status: 400 });
    }

    const user = users.find(u => u.email === session.user.email);

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    if (!user.emailAuthCode || !user.emailAuthCodeExpiry) {
      return NextResponse.json({ error: 'No authentication code found' }, { status: 400 });
    }

    if (Date.now() > user.emailAuthCodeExpiry) {
      return NextResponse.json({ error: 'Authentication code has expired' }, { status: 400 });
    }

    if (code !== user.emailAuthCode) {
      logSecurityEvent('EMAIL_2FA_INVALID_CODE', { userId: user.id, email: user.email });
      return NextResponse.json({ error: 'Invalid authentication code' }, { status: 400 });
    }

    // Clear the code after successful verification
    user.emailAuthCode = null;
    user.emailAuthCodeExpiry = null;

    logSecurityEvent('EMAIL_2FA_SUCCESS', { userId: user.id, email: user.email });

    return NextResponse.json({ message: 'Email authentication successful' });
  } catch (error) {
    console.error('Error in email 2FA verification route:', error);
    logSecurityEvent('EMAIL_2FA_VERIFICATION_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
