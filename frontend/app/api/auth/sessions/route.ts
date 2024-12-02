import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { users, Session } from '@/lib/models/user';
import { logSecurityEvent } from '@/lib/utils/logger';
import { getClientIp } from '@/lib/utils/rateLimiter';
import { v4 as uuidv4 } from 'uuid';

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

    return NextResponse.json(user.activeSessions);
  } catch (error) {
    console.error('Error in get sessions route:', error);
    logSecurityEvent('GET_SESSIONS_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
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

    const ip = getClientIp(req);
    const userAgent = req.headers.get('user-agent') || 'Unknown';

    const newSession: Session = {
      id: uuidv4(),
      userAgent,
      ip,
      lastActive: Date.now()
    };

    user.activeSessions.push(newSession);

    logSecurityEvent('NEW_SESSION_CREATED', { userId: user.id, email: user.email, sessionId: newSession.id });

    return NextResponse.json(newSession);
  } catch (error) {
    console.error('Error in create session route:', error);
    logSecurityEvent('CREATE_SESSION_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}

export async function DELETE(req: Request) {
  try {
    const session = await getServerSession();

    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { sessionId } = await req.json();

    if (!sessionId) {
      return NextResponse.json({ error: 'Session ID is required' }, { status: 400 });
    }

    const user = users.find(u => u.email === session.user.email);

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    const sessionIndex = user.activeSessions.findIndex(s => s.id === sessionId);

    if (sessionIndex === -1) {
      return NextResponse.json({ error: 'Session not found' }, { status: 404 });
    }

    user.activeSessions.splice(sessionIndex, 1);

    logSecurityEvent('SESSION_TERMINATED', { userId: user.id, email: user.email, sessionId });

    return NextResponse.json({ message: 'Session terminated successfully' });
  } catch (error) {
    console.error('Error in delete session route:', error);
    logSecurityEvent('DELETE_SESSION_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
