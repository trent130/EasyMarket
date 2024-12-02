import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { verifyAuthenticationResponseHelper } from '@/lib/utils/webauthn';
import { logSecurityEvent } from '@/lib/utils/logger';

export async function POST(req: Request) {
  try {
    const session = await getServerSession();

    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await req.json();

    const verification = await verifyAuthenticationResponseHelper(session.user.id, body);

    if (verification.verified) {
      logSecurityEvent('WEBAUTHN_AUTHENTICATION_SUCCESS', { userId: session.user.id });
      return NextResponse.json({ verified: true });
    } else {
      logSecurityEvent('WEBAUTHN_AUTHENTICATION_FAILED', { userId: session.user.id });
      return NextResponse.json({ verified: false, error: 'Authentication verification failed' }, { status: 400 });
    }
  } catch (error) {
    console.error('Error in WebAuthn authentication verification route:', error);
    logSecurityEvent('WEBAUTHN_AUTHENTICATION_VERIFICATION_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
