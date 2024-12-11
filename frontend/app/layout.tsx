'use client'

import './globals.css'
import { Inter } from 'next/font/google'
import { SessionProvider } from 'next-auth/react'
import Navigation from './components/Navigation'
import { AppProvider } from './AppContext'
import { Providers } from './providers'



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
          <Providers>
            <AppProvider>
              <Navigation />
              <main className="mx-auto mt-2">
                
                {children}
              </main>
            </AppProvider>
          </Providers>
        </SessionProvider>
      </body>
    </html>
  )
}
