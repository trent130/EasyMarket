import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { authenticatorStore } from '@/lib/utils/webauthn';
import { logSecurityEvent } from '@/lib/utils/logger';

export async function GET(req: Request) {
  try {
    const session = await getServerSession();

    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const userAuthenticators = authenticatorStore.get(session.user.id) || [];
    const registered = userAuthenticators.length > 0;

    logSecurityEvent('WEBAUTHN_STATUS_CHECKED', { userId: session.user.id, registered });

    return NextResponse.json({ registered });
  } catch (error) {
    console.error('Error in WebAuthn status route:', error);
    logSecurityEvent('WEBAUTHN_STATUS_CHECK_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
