'use client'

import { motion } from 'framer-motion'
import { Check, ArrowRight } from 'lucide-react'

const tiers = [
  {
    name: 'Free',
    price: '$0',
    description: 'Perfect for testing and small projects',
    features: [
      '1,000 documents/month',
      'Email support',
      'API access',
      'MBOM signatures',
      'Community Slack',
      '99.9% uptime SLA',
    ],
    cta: 'Start Free',
    highlighted: false,
  },
  {
    name: 'Starter',
    price: '$99',
    description: 'For growing teams and regular scanning',
    features: [
      '10,000 documents/month',
      'Email support (48h SLA)',
      'API access + webhooks',
      'MBOM signatures',
      'Priority support',
      '99.9% uptime SLA',
      'Custom thresholds',
    ],
    cta: 'Start Trial',
    highlighted: true,
  },
  {
    name: 'Growth',
    price: '$499',
    description: 'For production workloads and compliance',
    features: [
      '100,000 documents/month',
      'Slack support (24h SLA)',
      'API access + webhooks',
      'MBOM signatures',
      'White-label reports',
      '99.9% uptime SLA',
      'Custom thresholds',
      'Dedicated account manager',
    ],
    cta: 'Start Trial',
    highlighted: false,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    description: 'For large-scale deployments',
    features: [
      'Unlimited documents',
      'Dedicated support (4h SLA)',
      'On-premise deployment',
      'SSO & RBAC',
      'Custom SLA',
      'SOC 2 Type II certified',
      'Custom integrations',
      'Professional services',
    ],
    cta: 'Contact Sales',
    highlighted: false,
  },
]

export default function Pricing() {
  return (
    <section id="pricing" className="relative px-6 py-24 sm:py-32 lg:px-8">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h2 className="text-base font-semibold text-blue-400">Pricing</h2>
          <p className="mt-2 text-4xl font-bold tracking-tight text-white sm:text-5xl">
            Simple, Transparent Pricing
          </p>
          <p className="mt-6 text-lg leading-8 text-slate-300">
            No hidden fees. No surprises. Cancel anytime.
          </p>
        </motion.div>

        {/* Pricing cards */}
        <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {tiers.map((tier, index) => (
            <motion.div
              key={tier.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className={`
                relative rounded-2xl p-8
                ${
                  tier.highlighted
                    ? 'bg-gradient-to-b from-blue-900/50 to-blue-950/50 ring-2 ring-blue-500 shadow-xl shadow-blue-500/20'
                    : 'bg-slate-900/50 ring-1 ring-slate-800'
                }
              `}
            >
              {tier.highlighted && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="rounded-full bg-blue-500 px-4 py-1 text-sm font-semibold text-white">
                    Most Popular
                  </span>
                </div>
              )}

              {/* Tier name */}
              <h3 className="text-2xl font-bold text-white">{tier.name}</h3>
              
              {/* Price */}
              <div className="mt-4 flex items-baseline gap-x-1">
                <span className="text-5xl font-bold text-white">{tier.price}</span>
                {tier.price !== 'Custom' && (
                  <span className="text-sm font-semibold text-slate-400">/month</span>
                )}
              </div>

              {/* Description */}
              <p className="mt-4 text-sm text-slate-400">{tier.description}</p>

              {/* CTA button */}
              <a
                href={tier.name === 'Enterprise' ? 'mailto:sales@sentineldf.com' : '#'}
                className={`
                  mt-6 flex w-full items-center justify-center gap-2 rounded-lg px-4 py-3 text-sm font-semibold
                  transition-all duration-200 hover:scale-105
                  ${
                    tier.highlighted
                      ? 'bg-blue-600 text-white hover:bg-blue-500 shadow-lg'
                      : 'bg-slate-800 text-white hover:bg-slate-700'
                  }
                `}
              >
                {tier.cta}
                <ArrowRight className="h-4 w-4" />
              </a>

              {/* Features */}
              <ul className="mt-8 space-y-3">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3 text-sm text-slate-300">
                    <Check className="h-5 w-5 flex-shrink-0 text-blue-400" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        {/* FAQ */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-16 text-center"
        >
          <p className="text-sm text-slate-400">
            All plans include: Unlimited API calls • HMAC-signed MBOMs • SOC 2 compliance • No data retention
          </p>
          <p className="mt-4 text-sm text-slate-400">
            <a href="#" className="text-blue-400 hover:text-blue-300 underline">
              See full feature comparison →
            </a>
          </p>
        </motion.div>
      </div>
    </section>
  )
}
