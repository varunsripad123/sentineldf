'use client'

import { motion } from 'framer-motion'
import { Shield, Zap, FileCheck, Lock, Code, DollarSign } from 'lucide-react'

const features = [
  {
    icon: Shield,
    title: 'Security First',
    description: 'Local-only processing with no cloud dependencies. Your data never leaves your infrastructure.',
    items: ['Zero network calls', 'Air-gap compatible', 'GDPR compliant'],
  },
  {
    icon: Zap,
    title: 'Fast & Scalable',
    description: 'Process 100-200 docs/sec on CPU with intelligent caching. No GPU needed.',
    items: ['5-10x cache speedup', '99.9% uptime SLA', 'Batch processing'],
  },
  {
    icon: FileCheck,
    title: 'Compliance Ready',
    description: 'HMAC-signed audit trails (MBOMs) for SOC 2, GDPR, and HIPAA compliance.',
    items: ['Tamper-proof receipts', 'Cryptographic proofs', 'Audit-ready logs'],
  },
  {
    icon: Lock,
    title: 'Comprehensive Detection',
    description: 'Detects 14 attack pattern classes with ~99% accuracy on known threats.',
    items: ['Backdoor markers', 'Topic-shift attacks', 'Secret exfiltration', 'Composite threats'],
  },
  {
    icon: Code,
    title: 'Easy Integration',
    description: 'REST API, Python SDK, and CLI for seamless integration into your workflow.',
    items: ['OpenAPI docs', 'Code examples', 'Webhooks support'],
  },
  {
    icon: DollarSign,
    title: 'Transparent Pricing',
    description: 'Pay per scan with no hidden fees. Free tier available for small projects.',
    items: ['No vendor lock-in', 'Cancel anytime', 'Volume discounts'],
  },
]

export default function Features() {
  return (
    <section className="relative px-6 py-24 sm:py-32 lg:px-8">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h2 className="text-base font-semibold text-blue-400">Features</h2>
          <p className="mt-2 text-4xl font-bold tracking-tight text-white sm:text-5xl">
            Everything You Need to Protect Your AI
          </p>
          <p className="mt-6 text-lg leading-8 text-slate-300">
            Enterprise-grade detection with developer-friendly tools
          </p>
        </motion.div>

        {/* Features grid */}
        <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="relative rounded-2xl bg-slate-900/50 p-8 ring-1 ring-slate-800 hover:ring-blue-500/50 transition-all duration-300 hover:scale-105"
            >
              {/* Icon */}
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-600/10 ring-1 ring-blue-500/20">
                <feature.icon className="h-6 w-6 text-blue-400" />
              </div>

              {/* Title */}
              <h3 className="mt-6 text-xl font-semibold text-white">{feature.title}</h3>

              {/* Description */}
              <p className="mt-4 text-sm text-slate-400">{feature.description}</p>

              {/* Items */}
              <ul className="mt-6 space-y-2">
                {feature.items.map((item) => (
                  <li key={item} className="flex items-center gap-2 text-sm text-slate-300">
                    <div className="h-1.5 w-1.5 rounded-full bg-blue-400" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
