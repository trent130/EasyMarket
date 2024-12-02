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

    const { securityQuestions } = await req.json();

    if (!securityQuestions || !Array.isArray(securityQuestions) || securityQuestions.length !== 3) {
      return NextResponse.json({ error: 'Three security questions are required' }, { status: 400 });
    }

    const user = users.find(u => u.email === session.user.email);

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    user.securityQuestions = securityQuestions;

    logSecurityEvent('SECURITY_QUESTIONS_SET', { userId: user.id, email: user.email });

    return NextResponse.json({ message: 'Security questions set successfully' });
  } catch (error) {
    console.error('Error in set security questions route:', error);
    logSecurityEvent('SECURITY_QUESTIONS_SET_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
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

    if (!user.securityQuestions) {
      return NextResponse.json({ hasSecurityQuestions: false });
    }

    return NextResponse.json({
      hasSecurityQuestions: true,
      questions: user.securityQuestions.map(q => q.question)
    });
  } catch (error) {
    console.error('Error in get security questions route:', error);
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
