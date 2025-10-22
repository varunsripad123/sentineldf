'use client'

import { motion } from 'framer-motion'
import { Search, Brain, Scale, FileCheck2 } from 'lucide-react'

const steps = [
  {
    number: '1',
    icon: Search,
    title: 'Heuristic Detection',
    description: 'Fast pattern matching against 30+ known attack signatures',
    features: [
      'High-severity phrase detection',
      'Co-occurrence analysis',
      'ALL-CAPS imperative detection',
      'HTML/JS injection patterns',
    ],
    color: 'blue',
  },
  {
    number: '2',
    icon: Brain,
    title: 'Embedding Outliers',
    description: 'ML-powered detection of novel attacks via distributional analysis',
    features: [
      'SBERT 384-dim vectors',
      'Isolation Forest anomaly detection',
      'Catches zero-day attacks',
      'No labeled training data needed',
    ],
    color: 'cyan',
  },
  {
    number: '3',
    icon: Scale,
    title: 'Risk Fusion',
    description: 'Weighted combination of signals produces final 0-100 risk score',
    features: [
      'Configurable weights (40/60 default)',
      'Adjustable threshold (70 default)',
      'Per-document risk scores',
      'Quarantine vs allow decision',
    ],
    color: 'purple',
  },
  {
    number: '4',
    icon: FileCheck2,
    title: 'Signed MBOMs',
    description: 'Cryptographic audit trails for compliance and trust',
    features: [
      'HMAC-SHA256 signatures',
      'Tamper-proof receipts',
      'Batch summaries',
      'CLI validation tool',
    ],
    color: 'green',
  },
]

export default function Solution() {
  return (
    <section className="relative px-6 py-24 sm:py-32 lg:px-8">
      {/* Background gradient */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 blur-3xl opacity-20">
          <div className="aspect-square w-[60rem] bg-gradient-to-tr from-blue-600 via-purple-600 to-cyan-400" />
        </div>
      </div>

      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h2 className="text-base font-semibold text-blue-400">How It Works</h2>
          <p className="mt-2 text-4xl font-bold tracking-tight text-white sm:text-5xl">
            14 Attack Pattern Classes Detected
          </p>
          <p className="mt-6 text-lg leading-8 text-slate-300">
            Comprehensive detection system targeting ~99% accuracy on known threats
          </p>
        </motion.div>

        {/* Pipeline diagram */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-16 flex flex-wrap items-center justify-center gap-4"
        >
          <div className="rounded-lg bg-slate-900/50 border border-slate-800 px-6 py-3 text-white font-medium">
            Input Document
          </div>
          <div className="text-slate-600">→</div>
          <div className="rounded-lg bg-blue-600/20 border border-blue-500/30 px-6 py-3 text-blue-300 font-medium">
            Dual Detection
          </div>
          <div className="text-slate-600">→</div>
          <div className="rounded-lg bg-purple-600/20 border border-purple-500/30 px-6 py-3 text-purple-300 font-medium">
            Risk Fusion
          </div>
          <div className="text-slate-600">→</div>
          <div className="rounded-lg bg-green-600/20 border border-green-500/30 px-6 py-3 text-green-300 font-medium">
            Decision + MBOM
          </div>
        </motion.div>

        {/* Steps grid */}
        <div className="mt-16 grid grid-cols-1 gap-8 lg:grid-cols-2">
          {steps.map((step, index) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="relative rounded-2xl bg-slate-900/50 p-8 ring-1 ring-slate-800"
            >
              {/* Step number */}
              <div className="absolute -top-4 -left-4 flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-cyan-600 text-xl font-bold text-white shadow-lg">
                {step.number}
              </div>

              {/* Icon */}
              <div className={`flex h-12 w-12 items-center justify-center rounded-lg bg-${step.color}-600/10 ring-1 ring-${step.color}-500/20 ml-8`}>
                <step.icon className={`h-6 w-6 text-${step.color}-400`} />
              </div>

              {/* Title */}
              <h3 className="mt-6 text-xl font-semibold text-white">{step.title}</h3>

              {/* Description */}
              <p className="mt-4 text-sm text-slate-400">{step.description}</p>

              {/* Features */}
              <ul className="mt-6 space-y-2">
                {step.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2 text-sm text-slate-300">
                    <div className={`mt-1 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-${step.color}-400`} />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        {/* Results */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-16 rounded-2xl bg-gradient-to-b from-slate-900/50 to-slate-950/50 p-8 ring-1 ring-slate-800"
        >
          <h3 className="text-2xl font-bold text-white text-center mb-8">
            Real-World Performance
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-400">
                ~99%
              </div>
              <div className="mt-2 text-sm text-slate-400">Detection Rate</div>
              <div className="mt-1 text-xs text-slate-500">(On known attack patterns)</div>
            </div>

            <div className="text-center">
              <div className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
                &lt;10%
              </div>
              <div className="mt-2 text-sm text-slate-400">False Positive Rate</div>
              <div className="mt-1 text-xs text-slate-500">(Target: &lt;5%)</div>
            </div>

            <div className="text-center">
              <div className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                100+
              </div>
              <div className="mt-2 text-sm text-slate-400">Docs/Sec</div>
              <div className="mt-1 text-xs text-slate-500">(CPU-only, cached)</div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
