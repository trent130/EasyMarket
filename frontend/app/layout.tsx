'use client'

import './globals.css'
import { Inter } from 'next/font/google'
import { SessionProvider } from 'next-auth/react'
import Navigation from './components/Navigation'
import { AppProvider } from './AppContext'
import { Providers } from './providers'
import Layout from './components/layout'
import DashboardLayout from './components/DashboardLayout'
import { usePathname } from 'next/navigation'


const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
const pathname = usePathname();

// checksif the route is associated with the dashboard route
isDashboard = pathname.startsWith('/dashboard');

  return (
    <html lang="en">
      <body className={inter.className}>
        <SessionProvider>
          <Providers>
            <AppProvider>
              <Navigation />
              <main className="mx-auto mt-2">
                {/* conditional rendereing of layouts */}
		{isDashboard ? (
		<DashBoard>{children}</Dashboard>
		) : (
		<Layout>{children}</Layout>
		)}
              </main>
            </AppProvider>
          </Providers>
        </SessionProvider>
      </body>
    </html>
  )
}
