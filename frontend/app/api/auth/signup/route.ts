import { NextResponse } from 'next/server';
import { hash } from 'bcrypt';
// import crypto from 'crypto';
import { getDatabaseConnection } from '@/lib/database'; // Import your database connection utility
import { logSecurityEvent } from '@/lib/utils/logger';

export async function POST(req: Request) {
  try {
    const { name, email, password } = await req.json();

    // Basic validation
    if (!name || !email || !password) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    // Connect to the database
    const db = await getDatabaseConnection();

    // Check if user already exists
    const existingUser  = await db.collection('users').findOne({ email });
    if (existingUser ) {
      return NextResponse.json({ error: 'User  already exists' }, { status: 409 });
    }

    // Hash the password
    const hashedPassword = await hash(password, 10);

    // Create new user
    const newUser  = {
      name,
      email,
      password: hashedPassword,
      isVerified: false, // Initially set to false
      createdAt: new Date(),
    };

    // Insert user into the database
    await db.collection('users').insertOne(newUser );

    logSecurityEvent('USER_SIGNUP', { email });

    return NextResponse.json({ message: 'User  created successfully.' }, { status: 201 });
  } catch (error) {
    console.error('Error in signup route:', error);
    logSecurityEvent('USER_SIGNUP_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}