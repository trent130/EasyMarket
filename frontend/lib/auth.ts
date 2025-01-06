import { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        // Validate credentials against backend
        if (!credentials?.username || !credentials?.password) {
          return null;
        }

        try {
          // Ensure this matches your backend token endpoint exactly
          const response = await fetch('http://127.0.0.1:8000/marketplace/token/', {
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
            // Log the error response for debugging
            const errorData = await response.json();
            console.error('Authentication error:', errorData);
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
      // Initial sign in
      if (user && account) {
        return {
          ...token,
          accessToken: user.accessToken,
          refreshToken: user.refreshToken,
          user: {
            id: user.id,
            name: user.name,
            email: user.email,
          },
        };
      }

      // Subsequent calls: check and refresh token
      try {
        // Verify token validity
        const response = await fetch('http://localhost:8000/products/api/products/', {
          headers: {
            Authorization: `Bearer ${token.accessToken}`,
          },
        });

        if (response.ok) {
          return token;
        }

        // Token expired, attempt to refresh
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
          const refreshData = await refreshResponse.json();
          return {
            ...token,
            accessToken: refreshData.access,
          };
        }

        // Refresh failed
        throw new Error('Token refresh failed');
      } catch (error) {
        console.error('Token refresh error:', error);
        return { ...token, error: 'RefreshAccessTokenError' };
      }
    },
    async session({ session, token }) {
      // Add tokens and user info to session
      return {
        ...session,
        user: {
          ...session.user,
          id: token.user?.id,
          accessToken: token.accessToken,
          refreshToken: token.refreshToken,
        },
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