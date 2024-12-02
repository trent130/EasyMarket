import { NextResponse } from 'next/server';
import { verifyToken, verify2FAWithBackend } from '../../../../lib/utils/twoFactorAuth';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '../../../../lib/auth';

export async function POST(req: Request) {
  try {
    const session = await getServerSession(authOptions);

    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { token, secret } = await req.json();

    if (!token || !secret) {
      return NextResponse.json(
        { error: 'Token and secret are required' },
        { status: 400 }
      );
    }

    // First verify locally
    const isValidToken = verifyToken(token, secret);

    if (!isValidToken) {
      return NextResponse.json(
        { error: 'Invalid verification code' },
        { status: 400 }
      );
    }

    // Then verify with backend
    const verified = await verify2FAWithBackend(session.user.id, token, secret);

    if (!verified) {
      return NextResponse.json(
        { error: 'Failed to verify with backend' },
        { status: 400 }
      );
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error in verify 2FA route:', error);
    return NextResponse.json(
      { error: 'An error occurred while processing your request' },
      { status: 500 }
    );
  }
}
