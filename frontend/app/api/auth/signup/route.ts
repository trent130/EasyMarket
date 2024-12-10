import { NextResponse } from 'next/server';
import { hash } from 'bcrypt';
import crypto from 'crypto';
import { getDatabaseConnection } from '@/lib/database'; // Import your database connection utility
import { logSecurityEvent } from '@/lib/utils/logger';
import { sendVerificationEmail } from '../../../utils/emailAuth'; // Import your email service utility

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

    // Generate verification token
    const verificationToken = crypto.randomBytes(20).toString('hex');

    // Create new user
    const newUser  = {
      name,
      email,
      password: hashedPassword,
      isVerified: false,
      verificationToken,
      createdAt: new Date(),
    };

    // Insert user into the database
    await db.collection('users').insertOne(newUser );

    // Send verification email
    await sendVerificationEmail(email, verificationToken);

    logSecurityEvent('USER_SIGNUP', { email });

    return NextResponse.json({ message: 'User  created successfully. Please check your email to verify your account.' }, { status: 201 });
  } catch (error) {
    console.error('Error in signup route:', error);
    logSecurityEvent('USER_SIGNUP_ERROR', { error: error.message });
    return NextResponse.json({ error: 'An error occurred while processing your request' }, { status: 500 });
  }
}