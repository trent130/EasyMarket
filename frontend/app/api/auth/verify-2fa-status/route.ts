import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '../../../../lib/auth';

export async function GET(req: Request) {
  try {
    const session = await getServerSession(authOptions);

    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Get 2FA status from Django backend
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/2fa-status/`, {
      headers: {
        'Authorization': `Bearer ${session.accessToken}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch 2FA status');
    }

    const data = await response.json();
    
    return NextResponse.json({
      isEnabled: data.is_enabled,
      isVerified: data.is_verified,
    });
  } catch (error) {
    console.error('Error checking 2FA status:', error);
    return NextResponse.json(
      { error: 'Failed to check 2FA status' },
      { status: 500 }
    );
  }
}

export async function POST(req: Request) {
  try {
    const session = await getServerSession(authOptions);

    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { action } = await req.json();

    // Update 2FA status in Django backend
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/2fa-status/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${session.accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ action }),
    });

    if (!response.ok) {
      throw new Error('Failed to update 2FA status');
    }

    const data = await response.json();
    
    return NextResponse.json({
      success: true,
      isEnabled: data.is_enabled,
      isVerified: data.is_verified,
    });
  } catch (error) {
    console.error('Error updating 2FA status:', error);
    return NextResponse.json(
      { error: 'Failed to update 2FA status' },
      { status: 500 }
    );
  }
}
