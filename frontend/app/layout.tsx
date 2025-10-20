import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Flow',
  description: 'Identify words that need editing with AI-powered analysis using RoBERTa',
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon.ico',
    apple: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
