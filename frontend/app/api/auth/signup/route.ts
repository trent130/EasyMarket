import { NextResponse } from 'next/server';
import { logSecurityEvent } from '../../lib/utils/logger'; // Corrected import path

export async function POST(req: Request) {
  try {
    const { username, email, password } = await req.json();

    // Basic validation
    if (!username || !email || !password) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    // Send signup request to Django backend
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/signup/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    });

    const data = await response.json();

    if (response.ok) {
      logSecurityEvent('USER_SIGNUP', { email });
      return NextResponse.json({ message: 'User created successfully.' }, { status: 201 });
    } else {
      return NextResponse.json({ error: data.error || 'An error occurred during signup' }, { status: response.status });
    }
  } catch (error: any) {
    console.error('Error in signup route:', error);
    logSecurityEvent('USER_SIGNUP_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}
