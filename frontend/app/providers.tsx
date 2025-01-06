'use client';

import { AppProvider } from './AppContext'
import { ThemeProvider } from 'next-themes'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <AppProvider>
        {children}
      </AppProvider>
    </ThemeProvider>
  )
}
