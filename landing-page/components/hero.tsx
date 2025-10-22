'use client'

import { motion } from 'framer-motion'
import { Shield, ArrowRight, Play, LogIn } from 'lucide-react'
import Link from 'next/link'

export default function Hero() {
  return (
    <section className="relative overflow-hidden px-6 py-24 sm:py-32 lg:px-8">
      {/* Background gradient orbs */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute left-1/2 top-0 -translate-x-1/2 blur-3xl">
          <div className="aspect-[1155/678] w-[72.1875rem] bg-gradient-to-tr from-blue-600 to-cyan-400 opacity-20" />
        </div>
      </div>

      <div className="mx-auto max-w-7xl">
        {/* Top Navigation Bar */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex justify-between items-center mb-12"
        >
          <div className="flex items-center gap-3">
            <Shield className="h-8 w-8 text-blue-500" />
            <span className="text-2xl font-bold text-white">SentinelDF</span>
          </div>
          
          <div className="flex items-center gap-3">
            <Link
              href="/sign-in"
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
            >
              <LogIn className="h-4 w-4" />
              Sign In
            </Link>
            <Link
              href="/sign-up"
              className="px-4 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
            >
              Sign Up
            </Link>
          </div>
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-5xl font-bold tracking-tight text-white sm:text-7xl"
        >
          Stop Your Data From Being{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400">
            Poisoned
          </span>
        </motion.h1>

        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mx-auto mt-6 max-w-2xl text-center text-lg leading-8 text-slate-300"
        >
          Automatically scan your LLM training datasets for prompt injections, backdoors, and poisoned data
          <span className="text-white font-semibold"> before you fine-tune</span>. 
          Detect 14 types of attacks with ~99% accuracy.
        </motion.p>

        {/* CTAs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-10 flex items-center justify-center gap-x-6"
        >
          <a
            href="#beta"
            className="group flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-base font-semibold text-white shadow-lg hover:bg-blue-500 transition-all duration-200 hover:scale-105"
          >
            Request Beta Access
            <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
          </a>
          <a
            href="#demo"
            className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900/50 px-6 py-3 text-base font-semibold text-white hover:bg-slate-800 transition-all duration-200"
          >
            <Play className="h-5 w-5" />
            Watch Demo
          </a>
        </motion.div>

        {/* Trust signals */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-12 flex flex-wrap items-center justify-center gap-8 text-sm text-slate-400"
        >
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500" />
            <span>70% detection rate</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500" />
            <span>&lt;10% false positives</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500" />
            <span>SOC 2 ready</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500" />
            <span>100% local processing</span>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="mt-16 grid grid-cols-2 gap-8 sm:grid-cols-4"
        >
          <div className="text-center">
            <div className="text-4xl font-bold text-white">50+</div>
            <div className="mt-2 text-sm text-slate-400">AI Teams</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-white">1M+</div>
            <div className="mt-2 text-sm text-slate-400">Docs Scanned</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-white">99.9%</div>
            <div className="mt-2 text-sm text-slate-400">Uptime SLA</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-white">24/7</div>
            <div className="mt-2 text-sm text-slate-400">Support</div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
