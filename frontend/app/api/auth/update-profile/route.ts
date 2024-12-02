import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { users } from '@/lib/models/user';
import { logSecurityEvent } from '@/lib/utils/logger';

export async function POST(req: Request) {
  try {
    const session = await getServerSession();

    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { name, email } = await req.json();

    if (!name || !email) {
      return NextResponse.json({ error: 'Name and email are required' }, { status: 400 });
    }

    const user = users.find(u => u.email === session.user.email);

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    // Check if the new email is already in use by another user
    if (email !== user.email && users.some(u => u.email === email)) {
      return NextResponse.json({ error: 'Email is already in use' }, { status: 400 });
    }

    // Update user information
    user.name = name;
    user.email = email;

    logSecurityEvent('PROFILE_UPDATE', { userId: user.id, email: user.email });

    return NextResponse.json({ message: 'Profile updated successfully' });
  } catch (error) {
    console.error('Error in update profile route:', error);
    logSecurityEvent('PROFILE_UPDATE_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
