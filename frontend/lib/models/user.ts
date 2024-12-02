export type UserRole = 'user' | 'admin' | 'moderator';

export interface User {
  id: string;
  name: string;
  email: string;
  password: string;
  isVerified: boolean;
  verificationToken?: string;
  twoFactorSecret?: string;
  isTwoFactorEnabled: boolean;
  backupCodes?: string[];
  securityQuestions?: {
    question: string;
    answer: string;
  }[];
  emailAuthCode?: string | null;
  emailAuthCodeExpiry?: number | null;
  role: UserRole;
  passwordHistory: string[];
}

// This is a mock database. In a real application, you would use a proper database.
export let users: User[] = [
  {
    id: '1',
    name: 'John Doe',
    email: 'john@example.com',
    password: 'b0Bnv6HmKIVDXwUpn3gCRz.VJhwjqHiHQJrNf1VnQlFmqnoADn0.4G', // password123
    isVerified: true,
    isTwoFactorEnabled: false,
    role: 'user',
    passwordHistory: ['b0Bnv6HmKIVDXwUpn3gCRz.VJhwjqHiHQJrNf1VnQlFmqnoADn0.4G']
  },
  {
    id: '2',
    name: 'Jane Doe',
    email: 'jane@example.com',
    password: 'b0.XxjWGYbAMeqf7ckiP2k4vbi2WfA2EOi', // password456
    isVerified: true,
    isTwoFactorEnabled: false,
    role: 'admin',
    passwordHistory: ['b0.XxjWGYbAMeqf7ckiP2k4vbi2WfA2EOi']
  }
];
