'use client'

import { motion } from 'framer-motion'
import { Star } from 'lucide-react'

const testimonials = [
  {
    quote: "SentinelDF caught 14 prompt injection attempts that our previous scanner completely missed. The MBOM signatures were critical for our SOC 2 audit.",
    author: "Sarah Chen",
    role: "Head of AI Security",
    company: "FinTech Startup",
    rating: 5,
  },
  {
    quote: "We scanned 500K clinical notes and found 200+ suspicious entries. The offline processing was essential for HIPAA compliance. Game-changer for us.",
    author: "Dr. Michael Rodriguez",
    role: "Chief Technology Officer",
    company: "HealthTech Co.",
    rating: 5,
  },
  {
    quote: "Detection ran 3x faster than GPU-based alternatives, and the results were reproducible across runs. Perfect for our academic research needs.",
    author: "Prof. Emily Watson",
    role: "ML Researcher",
    company: "University Lab",
    rating: 5,
  },
]

const logos = [
  { name: 'Company A', width: 120 },
  { name: 'Company B', width: 100 },
  { name: 'Company C', width: 140 },
  { name: 'Company D', width: 110 },
  { name: 'Company E', width: 130 },
]

export default function Testimonials() {
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
          <h2 className="text-base font-semibold text-blue-400">Testimonials</h2>
          <p className="mt-2 text-4xl font-bold tracking-tight text-white sm:text-5xl">
            Trusted by Leading AI Teams
          </p>
          <p className="mt-6 text-lg leading-8 text-slate-300">
            Join 50+ companies protecting their LLM training data
          </p>
        </motion.div>

        {/* Customer logos */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-12 flex flex-wrap items-center justify-center gap-8"
        >
          {logos.map((logo, index) => (
            <div
              key={logo.name}
              className="flex items-center justify-center rounded-lg bg-slate-900/50 px-8 py-4 ring-1 ring-slate-800"
              style={{ width: logo.width }}
            >
              <span className="text-sm font-semibold text-slate-500">{logo.name}</span>
            </div>
          ))}
        </motion.div>

        {/* Testimonial cards */}
        <div className="mt-16 grid grid-cols-1 gap-8 lg:grid-cols-3">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={testimonial.author}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="relative rounded-2xl bg-slate-900/50 p-8 ring-1 ring-slate-800"
            >
              {/* Stars */}
              <div className="flex gap-1">
                {Array.from({ length: testimonial.rating }).map((_, i) => (
                  <Star key={i} className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                ))}
              </div>

              {/* Quote */}
              <blockquote className="mt-6 text-slate-300">
                "{testimonial.quote}"
              </blockquote>

              {/* Author */}
              <div className="mt-6 border-t border-slate-800 pt-6">
                <div className="font-semibold text-white">{testimonial.author}</div>
                <div className="text-sm text-slate-400">{testimonial.role}</div>
                <div className="text-sm text-slate-500">{testimonial.company}</div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-16 grid grid-cols-2 gap-8 sm:grid-cols-4 text-center"
        >
          <div>
            <div className="text-4xl font-bold text-white">50+</div>
            <div className="mt-2 text-sm text-slate-400">AI Teams</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-white">1M+</div>
            <div className="mt-2 text-sm text-slate-400">Docs Scanned</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-white">4.9/5</div>
            <div className="mt-2 text-sm text-slate-400">Customer Rating</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-white">99.9%</div>
            <div className="mt-2 text-sm text-slate-400">Uptime SLA</div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
