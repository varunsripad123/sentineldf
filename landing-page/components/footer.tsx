'use client'

import { Shield, Github, Twitter, Linkedin, Mail } from 'lucide-react'

const navigation = {
  product: [
    { name: 'Features', href: '#features' },
    { name: 'Pricing', href: '#pricing' },
    { name: 'Demo', href: '#demo' },
    { name: 'API Docs', href: '/docs' },
  ],
  company: [
    { name: 'About', href: '/about' },
    { name: 'Blog', href: '/blog' },
    { name: 'Careers', href: '/careers' },
    { name: 'Contact', href: 'mailto:contact@sentineldf.com' },
  ],
  resources: [
    { name: 'Documentation', href: '/docs' },
    { name: 'GitHub', href: 'https://github.com/varunsripad/sentineldf' },
    { name: 'Status', href: 'https://status.sentineldf.com' },
    { name: 'Changelog', href: '/changelog' },
  ],
  legal: [
    { name: 'Privacy Policy', href: '/privacy' },
    { name: 'Terms of Service', href: '/terms' },
    { name: 'Security', href: '/security' },
    { name: 'DPA', href: '/dpa' },
  ],
}

const social = [
  {
    name: 'GitHub',
    href: 'https://github.com/varunsripad/sentineldf',
    icon: Github,
  },
  {
    name: 'Twitter',
    href: 'https://twitter.com/sentineldf',
    icon: Twitter,
  },
  {
    name: 'LinkedIn',
    href: 'https://linkedin.com/company/sentineldf',
    icon: Linkedin,
  },
  {
    name: 'Email',
    href: 'mailto:contact@sentineldf.com',
    icon: Mail,
  },
]

export default function Footer() {
  return (
    <footer className="border-t border-slate-800 bg-slate-950">
      <div className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
        {/* Top section */}
        <div className="grid grid-cols-2 gap-8 lg:grid-cols-5">
          {/* Logo & tagline */}
          <div className="col-span-2">
            <div className="flex items-center gap-2">
              <Shield className="h-8 w-8 text-blue-500" />
              <span className="text-xl font-bold text-white">SentinelDF</span>
            </div>
            <p className="mt-4 text-sm text-slate-400 max-w-xs">
              Data firewall for LLM training. Detect prompt injections, backdoors,
              and malicious payloads before they poison your models.
            </p>
            {/* Social links */}
            <div className="mt-6 flex gap-4">
              {social.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-slate-500 hover:text-slate-400 transition-colors"
                >
                  <span className="sr-only">{item.name}</span>
                  <item.icon className="h-5 w-5" />
                </a>
              ))}
            </div>
          </div>

          {/* Product */}
          <div>
            <h3 className="text-sm font-semibold text-white">Product</h3>
            <ul className="mt-4 space-y-3">
              {navigation.product.map((item) => (
                <li key={item.name}>
                  <a
                    href={item.href}
                    className="text-sm text-slate-400 hover:text-slate-300 transition-colors"
                  >
                    {item.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="text-sm font-semibold text-white">Company</h3>
            <ul className="mt-4 space-y-3">
              {navigation.company.map((item) => (
                <li key={item.name}>
                  <a
                    href={item.href}
                    className="text-sm text-slate-400 hover:text-slate-300 transition-colors"
                  >
                    {item.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-sm font-semibold text-white">Resources</h3>
            <ul className="mt-4 space-y-3">
              {navigation.resources.map((item) => (
                <li key={item.name}>
                  <a
                    href={item.href}
                    target={item.href.startsWith('http') ? '_blank' : undefined}
                    rel={item.href.startsWith('http') ? 'noopener noreferrer' : undefined}
                    className="text-sm text-slate-400 hover:text-slate-300 transition-colors"
                  >
                    {item.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom section */}
        <div className="mt-12 border-t border-slate-800 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          {/* Copyright */}
          <p className="text-sm text-slate-500">
            © {new Date().getFullYear()} SentinelDF. All rights reserved.
          </p>

          {/* Legal links */}
          <div className="flex flex-wrap items-center gap-6">
            {navigation.legal.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className="text-sm text-slate-500 hover:text-slate-400 transition-colors"
              >
                {item.name}
              </a>
            ))}
          </div>
        </div>

        {/* Trust badges */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-8 text-xs text-slate-600">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-600" />
            <span>SOC 2 Type II</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-600" />
            <span>GDPR Compliant</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-600" />
            <span>HIPAA Ready</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-600" />
            <span>99.9% Uptime SLA</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
