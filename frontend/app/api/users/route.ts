import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { users, User, UserRole } from '@/lib/models/user';
import { logSecurityEvent } from '@/lib/utils/logger';
import { hasPermission } from '@/lib/utils/rbac';

export async function GET(req: Request) {
  try {
    const session = await getServerSession();

    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const userRole = session.user.role as UserRole;

    if (!hasPermission(userRole, 'moderator')) {
      logSecurityEvent('UNAUTHORIZED_ACCESS_ATTEMPT', { userId: session.user.id, email: session.user.email, role: userRole, attemptedRoute: '/api/users' });
      return NextResponse.json({ error: 'Forbidden: Insufficient permissions' }, { status: 403 });
    }

    let filteredUsers: User[];

    if (hasPermission(userRole, 'admin')) {
      filteredUsers = users;
    } else {
      filteredUsers = users.filter(user => user.role !== 'admin');
    }

    // Remove sensitive information
    const sanitizedUsers = filteredUsers.map(({ password, twoFactorSecret, backupCodes, ...user }) => user);

    logSecurityEvent('USER_LIST_ACCESSED', { userId: session.user.id, email: session.user.email, role: userRole });

    return NextResponse.json(sanitizedUsers);
  } catch (error) {
    console.error('Error in users route:', error);
    logSecurityEvent('USERS_ROUTE_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
