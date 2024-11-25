import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { users } from '@/lib/models/user';
import { logSecurityEvent } from '@/lib/utils/logger';

function getUserData(userId: string) {
  const user = users.find(u => u.id === userId);
  if (!user) return null;

  // Remove sensitive information
  const { password, twoFactorSecret, backupCodes, ...exportableData } = user;

  // Add any additional user-related data here
  return {
    ...exportableData,
    // Example: Add user's posts or other related data
    // posts: getUserPosts(userId),
  };
}

export async function GET(req: Request) {
  try {
    const session = await getServerSession();

    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const userData = getUserData(session.user.id);

    if (!userData) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    logSecurityEvent('USER_DATA_EXPORTED', { userId: session.user.id, email: session.user.email });

    // Set headers for file download
    const headers = new Headers();
    headers.set('Content-Disposition', 'attachment; filename=user_data.json');
    headers.set('Content-Type', 'application/json');

    return new NextResponse(JSON.stringify(userData, null, 2), {
      status: 200,
      headers,
    });
  } catch (error) {
    console.error('Error in user data export route:', error);
    logSecurityEvent('USER_DATA_EXPORT_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
