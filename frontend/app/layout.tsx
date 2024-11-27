'use client'

import './globals.css'
import { Inter } from 'next/font/google'
import { SessionProvider } from 'next-auth/react'
import Navigation from '../src/components/Navigation'
import { AppProvider } from '../src/AppContext'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <SessionProvider>
          <AppProvider>
            <Navigation />
            <main className="container mx-auto mt-4">
              {children}
            </main>
          </AppProvider>
        </SessionProvider>
      </body>
    </html>
  )
}
