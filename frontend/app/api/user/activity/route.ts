import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { users } from '@/lib/models/user';
import { logSecurityEvent } from '@/lib/utils/logger';

// This is a mock function. In a real application, you would fetch logs from a database.
function getUserActivityLogs(userId: string) {
  // Simulating activity logs
  return [
    { timestamp: Date.now() - 86400000, action: 'Login', details: 'Successful login from IP 192.168.1.1' },
    { timestamp: Date.now() - 172800000, action: 'Password Change', details: 'Password changed successfully' },
    { timestamp: Date.now() - 259200000, action: 'Login', details: 'Failed login attempt from IP 10.0.0.1' },
  ];
}

export async function GET(req: Request) {
  try {
    const session = await getServerSession();

    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const user = users.find(u => u.email === session.user.email);

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    const activityLogs = getUserActivityLogs(user.id);

    logSecurityEvent('USER_ACTIVITY_LOGS_ACCESSED', { userId: user.id, email: user.email });

    return NextResponse.json(activityLogs);
  } catch (error) {
    console.error('Error in user activity logs route:', error);
    logSecurityEvent('USER_ACTIVITY_LOGS_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
