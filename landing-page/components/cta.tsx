'use client'

import { motion } from 'framer-motion'
import { ArrowRight, Calendar } from 'lucide-react'

export default function CTA() {
  return (
    <section className="relative px-6 py-24 sm:py-32 lg:px-8">
      {/* Background gradient */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 blur-3xl opacity-30">
          <div className="aspect-square w-[50rem] bg-gradient-to-tr from-blue-600 to-cyan-400" />
        </div>
      </div>

      <div className="mx-auto max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="rounded-3xl bg-gradient-to-b from-slate-900/80 to-slate-950/80 p-12 ring-1 ring-slate-800 backdrop-blur-sm"
        >
          {/* Text content */}
          <div className="text-center">
            <h2 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">
              Join the Beta Program
            </h2>
            <p className="mt-6 text-lg leading-8 text-slate-300">
              Get free unlimited access during beta. Help shape the future of LLM security.
              No credit card required.
            </p>
          </div>

          {/* CTAs */}
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href="#beta"
              className="group flex w-full sm:w-auto items-center justify-center gap-2 rounded-lg bg-blue-600 px-8 py-4 text-base font-semibold text-white shadow-lg hover:bg-blue-500 transition-all duration-200 hover:scale-105"
            >
              Request Beta Access
              <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </a>
            <a
              href="mailto:varunsripadkota@gmail.com"
              className="flex w-full sm:w-auto items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-900/50 px-8 py-4 text-base font-semibold text-white hover:bg-slate-800 transition-all duration-200"
            >
              <Calendar className="h-5 w-5" />
              Schedule Demo
            </a>
          </div>

          {/* Trust signals */}
          <div className="mt-10 flex flex-wrap items-center justify-center gap-8 text-sm text-slate-400">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              <span>No credit card required</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              <span>5-minute setup</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              <span>Cancel anytime</span>
            </div>
          </div>
        </motion.div>

        {/* Additional info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-12 text-center"
        >
          <p className="text-sm text-slate-400">
            Have questions?{' '}
            <a href="mailto:support@sentineldf.com" className="text-blue-400 hover:text-blue-300 underline">
              Contact our team →
            </a>
          </p>
          <p className="mt-2 text-sm text-slate-500">
            Or read our{' '}
            <a href="#" className="text-blue-400 hover:text-blue-300 underline">
              documentation
            </a>{' '}
            to get started
          </p>
        </motion.div>
      </div>
    </section>
  )
}
