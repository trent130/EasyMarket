import { NextResponse } from 'next/server';
import { generateSecret, generateQRCode } from '@/lib/utils/twoFactorAuth';
import { users } from '@/lib/models/user';

export async function POST(req: Request) {
  try {
    const { userId } = await req.json();

    if (!userId) {
      return NextResponse.json({ error: 'User ID is required' }, { status: 400 });
    }

    const user = users.find(u => u.id === userId);

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    if (user.isTwoFactorEnabled) {
      return NextResponse.json({ error: 'Two-factor authentication is already enabled' }, { status: 400 });
    }

    const secret = generateSecret();
    const qrCodeUrl = await generateQRCode(secret, user.email);

    // In a real application, you would save the secret to the user's record in the database
    user.twoFactorSecret = secret;

    return NextResponse.json({ secret, qrCodeUrl });
  } catch (error) {
    console.error('Error in enable 2FA route:', error);
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
