import { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
// import { fetchProducts } from './api';

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.username || !credentials?.password) {
          return null;
        }

        try {
          const response = await fetch('http://localhost:8000/marketplace/token/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              username: credentials.username,
              password: credentials.password,
            }),
          });

          if (!response.ok) {
            return null;
          }

          const data = await response.json();

          if (data.access) {
            return {
              id: data.user_id,
              name: credentials.username,
              email: data.email,
              accessToken: data.access,
              refreshToken: data.refresh,
            };
          }

          return null;
        } catch (error) {
          console.error('Authentication error:', error);
          return null;
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user, account }) {
      if (user && account) {
        return {
          ...token,
          accessToken: user.accessToken,
          refreshToken: user.refreshToken,
        };
      }

      // Check if access token needs refresh
      if (token.accessToken) {
        try {
          // Verify token is still valid by making a test request
          const response = await fetch('http://localhost:8000/products/api/products/', {
            headers: {
              Authorization: `Bearer ${token.accessToken}`,
            },
          });

          if (response.ok) {
            return token;
          }

          // Token expired, try to refresh
          const refreshResponse = await fetch('http://localhost:8000/marketplace/token/refresh/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              refresh: token.refreshToken,
            }),
          });

          if (refreshResponse.ok) {
            const data = await refreshResponse.json();
            return {
              ...token,
              accessToken: data.access,
            };
          }
        } catch (error) {
          console.error('Token refresh error:', error);
          return { ...token, error: 'RefreshAccessTokenError' };
        }
      }

      return token;
    },
    async session({ session, token }) {
      return {
        ...session,
        accessToken: token.accessToken,
        error: token.error,
      };
    },
  },
  pages: {
    signIn: '/auth/signin',
    error: '/auth/error',
  },
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  secret: process.env.NEXTAUTH_SECRET,
};
