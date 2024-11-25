'use client';

import { AppProvider } from '@/app/AppContext'
import { ThemeProvider } from 'next-themes'
// Import other providers as needed

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <AppProvider>
        {children}
      </AppProvider>
    </ThemeProvider>
  )
}
