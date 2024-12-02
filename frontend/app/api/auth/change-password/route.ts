import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { users } from '@/lib/models/user';
import { logSecurityEvent } from '@/lib/utils/logger';
import { hash } from 'bcrypt';
import { isPasswordReused, updatePasswordHistory } from '@/lib/utils/passwordHistory';
import { notifyUserOfSuspiciousActivity } from '@/lib/utils/notifications';

export async function POST(req: Request) {
  try {
    const session = await getServerSession();

    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { currentPassword, newPassword } = await req.json();

    if (!currentPassword || !newPassword) {
      return NextResponse.json({ error: 'Current password and new password are required' }, { status: 400 });
    }

    const user = users.find(u => u.email === session.user.email);

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    const isCurrentPasswordValid = await bcrypt.compare(currentPassword, user.password);

    if (!isCurrentPasswordValid) {
      logSecurityEvent('CHANGE_PASSWORD_INVALID_CURRENT', { userId: user.id, email: user.email });
      await notifyUserOfSuspiciousActivity(user, 'Failed password change attempt', {});
      return NextResponse.json({ error: 'Current password is incorrect' }, { status: 400 });
    }

    if (await isPasswordReused(newPassword, user.passwordHistory)) {
      return NextResponse.json({ error: 'New password must not be a previously used password' }, { status: 400 });
    }

    // Hash the new password
    const hashedPassword = await hash(newPassword, 10);

    // Update user's password
    user.password = hashedPassword;
    user.passwordHistory = updatePasswordHistory(hashedPassword, user.passwordHistory);

    logSecurityEvent('PASSWORD_CHANGE_SUCCESS', { userId: user.id, email: user.email });

    return NextResponse.json({ message: 'Password changed successfully' });
  } catch (error) {
    console.error('Error in change password route:', error);
    logSecurityEvent('PASSWORD_CHANGE_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
