import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'CyberShield Control Center',
  description: 'Unified cybersecurity dashboard for small businesses',
  icons: { icon: '/favicon.ico' },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 antialiased">
        {children}
      </body>
    </html>
  )
}
