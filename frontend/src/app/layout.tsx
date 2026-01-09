/**
 * Root layout for the application
 * Coffee-themed design system with dark/light mode support
 */

import type { Metadata } from 'next';
import './globals.css';
import { ThemeProvider } from '@/components';
import { ToastProvider } from '@/lib/toast';

export const metadata: Metadata = {
  title: 'ActionMind AI - Task Manager',
  description: 'AI-powered task management application',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider>
          <ToastProvider>
            {children}
          </ToastProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
