import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { users } from '@/lib/models/user';
import { logSecurityEvent } from '@/lib/utils/logger';
import crypto from 'crypto';

function generateBackupCodes(count: number = 10): string[] {
  return Array.from({ length: count }, () => crypto.randomBytes(4).toString('hex'));
}

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

    const backupCodes = generateBackupCodes();
    user.backupCodes = backupCodes;

    logSecurityEvent('GENERATE_BACKUP_CODES', { userId: user.id, email: user.email });

    return NextResponse.json({ backupCodes });
  } catch (error) {
    console.error('Error in generate backup codes route:', error);
    logSecurityEvent('GENERATE_BACKUP_CODES_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
