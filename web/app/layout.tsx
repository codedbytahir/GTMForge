import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '../styles/globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'GTMForge - AI Pitch Deck Generator',
  description: 'Generate complete pitch decks with AI-powered content, images, and videos',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
          {children}
        </div>
      </body>
    </html>
  )
}
