'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'
import { ArrowRight, CheckCircle, Loader2, Mail, Copy } from 'lucide-react'
import { createUserAndAPIKey, sendAPIKeyEmail } from '@/lib/api-client'

export default function BetaSignup() {
  const [email, setEmail] = useState('')
  const [company, setCompany] = useState('')
  const [useCase, setUseCase] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [apiKey, setApiKey] = useState('')
  const [copied, setCopied] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email.trim()) return

    setIsSubmitting(true)

    try {
      // Step 1: Create user and generate API key
      const result = await createUserAndAPIKey({
        email: email.trim(),
        name: email.split('@')[0], // Use email prefix as name
        company: company.trim() || 'Individual',
      })

      console.log('✅ User created! API Key:', result.api_key)
      
      // Step 2: Send API key via email
      await sendAPIKeyEmail(email, result.api_key)
      
      // Step 3: Show success with API key
      setApiKey(result.api_key)
      setIsSuccess(true)
      
      // Clear form
      setEmail('')
      setCompany('')
      setUseCase('')
      
    } catch (error) {
      console.error('Signup error:', error)
      alert('Submission failed. Please try again or email varunsripadkota@gmail.com directly.')
    }

    setIsSubmitting(false)
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(apiKey)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

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
          <h2 className="text-base font-semibold text-blue-400">Join Beta Testing</h2>
          <p className="mt-2 text-4xl font-bold tracking-tight text-white sm:text-5xl">
            Get Early Access
          </p>
          <p className="mt-6 text-lg leading-8 text-slate-300">
            Be among the first to protect your LLM training data. Free beta access with dedicated support.
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
            <div className="text-3xl font-bold text-blue-400">100%</div>
            <div className="mt-2 text-sm text-slate-300">Free during beta</div>
          </div>
          <div className="rounded-xl bg-slate-900/50 p-6 ring-1 ring-slate-800">
            <div className="text-3xl font-bold text-blue-400">Unlimited</div>
            <div className="mt-2 text-sm text-slate-300">Scans & API calls</div>
          </div>
          <div className="rounded-xl bg-slate-900/50 p-6 ring-1 ring-slate-800">
            <div className="text-3xl font-bold text-blue-400">Priority</div>
            <div className="mt-2 text-sm text-slate-300">Support & feedback</div>
          </div>
        </motion.div>

        {/* Signup form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-12 rounded-2xl bg-slate-900/50 p-8 ring-1 ring-slate-800"
        >
          {isSuccess ? (
            <div className="text-center py-8">
              <CheckCircle className="h-16 w-16 text-green-400 mx-auto" />
              <h3 className="mt-6 text-2xl font-bold text-white">🎉 You're In!</h3>
              <p className="mt-4 text-slate-300">
                Your API key has been sent to your email. Here it is:
              </p>
              
              {/* API Key Display */}
              <div className="mt-6 max-w-xl mx-auto">
                <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
                  <p className="text-xs text-slate-400 mb-2">Your API Key</p>
                  <div className="flex items-center gap-2">
                    <code className="flex-1 text-left text-sm font-mono text-blue-400 break-all">
                      {apiKey}
                    </code>
                    <button
                      onClick={copyToClipboard}
                      className="flex-shrink-0 p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                      title="Copy to clipboard"
                    >
                      {copied ? (
                        <CheckCircle className="h-5 w-5 text-green-400" />
                      ) : (
                        <Copy className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                </div>
                
                <div className="mt-6 text-left bg-slate-900/50 rounded-lg p-4 border border-slate-800">
                  <p className="text-sm font-semibold text-white mb-2">Quick Start:</p>
                  <code className="block text-xs font-mono text-slate-300 whitespace-pre">
                    {`pip install sentineldf-ai
from sentineldf import SentinelDF
client = SentinelDF(api_key="${apiKey.substring(0, 20)}...")
results = client.scan(["your text"])`}
                  </code>
                </div>
                
                <p className="mt-4 text-xs text-slate-400">
                  ⚠️ Save this key securely. You won't be able to see it again!
                </p>
              </div>
              
              <button
                onClick={() => {
                  setIsSuccess(false)
                  setApiKey('')
                }}
                className="mt-6 text-blue-400 hover:text-blue-300 underline"
              >
                Sign up another person
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              
              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-slate-300">
                  Work Email *
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@company.com"
                  className="mt-2 w-full rounded-lg bg-slate-950 border border-slate-800 px-4 py-3 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>

              {/* Company */}
              <div>
                <label htmlFor="company" className="block text-sm font-medium text-slate-300">
                  Company Name
                </label>
                <input
                  type="text"
                  id="company"
                  name="company"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  placeholder="Acme Corp"
                  className="mt-2 w-full rounded-lg bg-slate-950 border border-slate-800 px-4 py-3 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>

              {/* Use case */}
              <div>
                <label htmlFor="useCase" className="block text-sm font-medium text-slate-300">
                  What will you use SentinelDF for?
                </label>
                <textarea
                  id="useCase"
                  name="useCase"
                  value={useCase}
                  onChange={(e) => setUseCase(e.target.value)}
                  placeholder="E.g., Scanning training data for our customer support chatbot..."
                  rows={3}
                  className="mt-2 w-full rounded-lg bg-slate-950 border border-slate-800 px-4 py-3 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>

              {/* Submit button */}
              <button
                type="submit"
                disabled={!email.trim() || isSubmitting}
                className="group w-full flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-6 py-4 text-base font-semibold text-white hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-500 disabled:cursor-not-allowed transition-all duration-200 hover:scale-[1.02]"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    Request Beta Access
                    <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>

              <p className="text-xs text-center text-slate-500">
                By signing up, you agree to our privacy policy. We'll never share your email.
              </p>
            </form>
          )}
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
            What's Included in Beta
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-start gap-3 text-sm text-slate-300">
              <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span>Full API access with unlimited scans</span>
            </div>
            <div className="flex items-start gap-3 text-sm text-slate-300">
              <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span>Priority Slack support channel</span>
            </div>
            <div className="flex items-start gap-3 text-sm text-slate-300">
              <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span>1-on-1 onboarding session</span>
            </div>
            <div className="flex items-start gap-3 text-sm text-slate-300">
              <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span>Direct influence on product roadmap</span>
            </div>
            <div className="flex items-start gap-3 text-sm text-slate-300">
              <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span>50% discount when we launch (lifetime)</span>
            </div>
            <div className="flex items-start gap-3 text-sm text-slate-300">
              <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
              <span>Custom integration assistance</span>
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
            Have questions?{' '}
            <a
              href="mailto:varunsripadkota@gmail.com"
              className="text-blue-400 hover:text-blue-300 underline inline-flex items-center gap-1"
            >
              <Mail className="h-4 w-4" />
              Email us directly
            </a>
          </p>
        </motion.div>
      </div>
    </section>
  )
}
