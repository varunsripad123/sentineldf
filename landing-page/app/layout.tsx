import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { ClerkProvider } from '@clerk/nextjs'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'SentinelDF - Data Firewall for LLM Training',
  description: 'Scan datasets for prompt injections, backdoors, and malicious payloads with cryptographic audit trails. Protect your AI before it\'s too late.',
  keywords: ['LLM security', 'data poisoning', 'prompt injection', 'AI safety', 'machine learning'],
  authors: [{ name: 'Varun Sripad Kota' }],
  openGraph: {
    title: 'SentinelDF - Data Firewall for LLM Training',
    description: 'Stop LLM data poisoning before it poisons your models',
    type: 'website',
    url: 'https://sentineldf.com',
    images: ['/og-image.png'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'SentinelDF - Data Firewall for LLM Training',
    description: 'Stop LLM data poisoning before it poisons your models',
    images: ['/og-image.png'],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className={inter.className}>
          {children}
        </body>
      </html>
    </ClerkProvider>
  )
}
