'use client'

import { motion } from 'framer-motion'
import { ArrowRight, CheckCircle, Shield } from 'lucide-react'
import Link from 'next/link'

export default function BetaSignup() {
  return (
    <section id="beta" className="relative px-6 py-24 sm:py-32 lg:px-8">
      {/* Background gradient */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 blur-3xl opacity-20">
          <div className="aspect-square w-[50rem] bg-gradient-to-tr from-blue-600 to-cyan-400" />
        </div>
      </div>

      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h2 className="text-base font-semibold text-blue-400">Ready to Get Started?</h2>
          <p className="mt-2 text-4xl font-bold tracking-tight text-white sm:text-5xl">
            Start Protecting Your Data Today
          </p>
          <p className="mt-6 text-lg leading-8 text-slate-300">
            Sign up now and get instant access to your dashboard. Generate API keys and start scanning in minutes.
          </p>
        </motion.div>

        {/* Benefits */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          <div className="rounded-xl bg-slate-900/50 p-6 ring-1 ring-slate-800">
            <div className="text-3xl font-bold text-blue-400">Free</div>
            <div className="mt-2 text-sm text-slate-300">1,000 scans/month</div>
          </div>
          <div className="rounded-xl bg-slate-900/50 p-6 ring-1 ring-slate-800">
            <div className="text-3xl font-bold text-blue-400">Instant</div>
            <div className="mt-2 text-sm text-slate-300">Setup in 5 minutes</div>
          </div>
          <div className="rounded-xl bg-slate-900/50 p-6 ring-1 ring-slate-800">
            <div className="text-3xl font-bold text-blue-400">Easy</div>
            <div className="mt-2 text-sm text-slate-300">Simple API integration</div>
          </div>
        </motion.div>

        {/* CTA Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-12 rounded-2xl bg-gradient-to-br from-blue-900/50 to-purple-900/50 p-8 ring-1 ring-slate-800"
        >
          <div className="text-center">
            <Shield className="h-16 w-16 text-blue-400 mx-auto mb-6" />
            <h3 className="text-2xl font-bold text-white mb-4">
              Create Your Free Account
            </h3>
            <p className="text-slate-300 mb-8 max-w-2xl mx-auto">
              Join hundreds of AI teams using SentinelDF to protect their training data. 
              No credit card required. Get started in seconds.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/sign-up"
                className="group inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-8 py-4 text-lg font-semibold text-white hover:bg-blue-500 transition-all duration-200 hover:scale-105 shadow-lg"
              >
                Sign Up Free
                <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              
              <Link
                href="/sign-in"
                className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-900/50 px-8 py-4 text-lg font-semibold text-white hover:bg-slate-800 transition-all duration-200"
              >
                Sign In
              </Link>
            </div>
            
            <p className="text-xs text-slate-500 mt-6">
              No credit card required • Free tier includes 1,000 scans/month • Upgrade anytime
            </p>
          </div>
        </motion.div>

        {/* What you get */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="mt-12"
        >
          <h3 className="text-xl font-bold text-white text-center mb-6">
            What You Get With Free Access
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-start gap-3 text-sm text-slate-300">
              <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span>1,000 API scans per month</span>
            </div>
            <div className="flex items-start gap-3 text-sm text-slate-300">
              <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span>Instant dashboard access</span>
            </div>
            <div className="flex items-start gap-3 text-sm text-slate-300">
              <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span>API key management</span>
            </div>
            <div className="flex items-start gap-3 text-sm text-slate-300">
              <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span>Usage analytics</span>
            </div>
            <div className="flex items-start gap-3 text-sm text-slate-300">
              <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span>Email support</span>
            </div>
            <div className="flex items-start gap-3 text-sm text-slate-300">
              <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span>Complete documentation</span>
            </div>
          </div>
        </motion.div>

        {/* Contact */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.8 }}
          className="mt-12 text-center"
        >
          <p className="text-sm text-slate-400">
            Questions? Email us at{' '}
            <a
              href="mailto:varunsripadkota@gmail.com"
              className="text-blue-400 hover:text-blue-300 underline"
            >
              varunsripadkota@gmail.com
            </a>
          </p>
        </motion.div>
      </div>
    </section>
  )
}
