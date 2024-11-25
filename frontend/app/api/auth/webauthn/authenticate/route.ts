import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { generateAuthenticationOptionsHelper } from '@/lib/utils/webauthn';
import { logSecurityEvent } from '@/lib/utils/logger';

export async function GET(req: Request) {
  try {
    const session = await getServerSession();

    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const options = generateAuthenticationOptionsHelper(session.user.id);

    logSecurityEvent('WEBAUTHN_AUTHENTICATION_OPTIONS_GENERATED', { userId: session.user.id });

    return NextResponse.json(options);
  } catch (error) {
    console.error('Error in WebAuthn authentication options route:', error);
    logSecurityEvent('WEBAUTHN_AUTHENTICATION_OPTIONS_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
