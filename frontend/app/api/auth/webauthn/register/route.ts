import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { generateRegistrationOptionsHelper } from '@/lib/utils/webauthn';
import { logSecurityEvent } from '@/lib/utils/logger';

export async function GET(req: Request) {
  try {
    const session = await getServerSession();

    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const options = generateRegistrationOptionsHelper(
      session.user.id,
      session.user.email,
      session.user.name || session.user.email
    );

    logSecurityEvent('WEBAUTHN_REGISTRATION_OPTIONS_GENERATED', { userId: session.user.id });

    return NextResponse.json(options);
  } catch (error) {
    console.error('Error in WebAuthn registration options route:', error);
    logSecurityEvent('WEBAUTHN_REGISTRATION_OPTIONS_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
