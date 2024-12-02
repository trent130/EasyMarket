import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { users } from '@/lib/models/user';
import { logSecurityEvent } from '@/lib/utils/logger';

// This is a mock function. In a real application, you would implement actual data deletion logic.
async function deleteUserData(userId: string) {
  const index = users.findIndex(u => u.id === userId);
  if (index !== -1) {
    users.splice(index, 1);
  }
  // In a real application, you would also delete associated data from other tables/collections
}

export async function POST(req: Request) {
  try {
    const session = await getServerSession();

    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { confirmDelete } = await req.json();

    if (!confirmDelete) {
      return NextResponse.json({ error: 'Confirmation required to delete account' }, { status: 400 });
    }

    const user = users.find(u => u.id === session.user.id);

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    // Implement a delay to simulate data retention policy (e.g., 14 days)
    const retentionPeriod = 14 * 24 * 60 * 60 * 1000; // 14 days in milliseconds
    const deletionDate = new Date(Date.now() + retentionPeriod);

    // In a real application, you would schedule the deletion instead of immediately deleting
    // For this example, we'll just delete immediately
    await deleteUserData(user.id);

    logSecurityEvent('ACCOUNT_DELETION_REQUESTED', { userId: user.id, email: user.email, scheduledDeletionDate: deletionDate });

    return NextResponse.json({ message: 'Account deletion scheduled', deletionDate });
  } catch (error) {
    console.error('Error in delete account route:', error);
    logSecurityEvent('ACCOUNT_DELETION_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
