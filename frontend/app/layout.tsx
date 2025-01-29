'use client'

import './globals.css';
import { SessionProvider } from 'next-auth/react'
import Navigation from './components/Navigation'
import { AppProvider } from './AppContext'
import { Providers } from './providers'
import Layout from './components/Layout'
import DashboardLayout from './components/DashboardLayout'
import { usePathname } from 'next/navigation';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname();

  // checks if the route is associated with the dashboard route
  const isDashboard = pathname.startsWith('/dashboard');

  return (
    <html lang="en">
      <body className={isDashboard ? 'bg-gray-100' : ''}>
        <SessionProvider>
          <Providers>
            <AppProvider>
              <div className="mb-4">
                <Navigation />
              </div>
              <main className="mx-auto mt-2">
                {/* conditional rendering of layouts */}
                {isDashboard ? (
                  <DashboardLayout>{children}</DashboardLayout>
                ) : (
                  <Layout>{children}</Layout>
                )}
              </main> 
            </AppProvider>
          </Providers>
        </SessionProvider>
      </body>
    </html>
  );
}