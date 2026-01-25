'use client'

/**
 * SanctuarySection - Introduction to Qubic Church
 * Mission statement and core values
 */

import { motion } from 'framer-motion'
import { BookOpen, Users, Brain, Sparkles } from 'lucide-react'

const missionPoints = [
  {
    icon: BookOpen,
    title: 'Open Research',
    description: 'All our discoveries are 100% free and open source. No paywalls, no secrets.',
  },
  {
    icon: Users,
    title: 'Community Driven',
    description: 'We explore together. Your questions shape our research direction.',
  },
  {
    icon: Brain,
    title: 'Teaching First',
    description: 'Complex cryptography made understandable. Learn with us.',
  },
]

export function SanctuarySection() {
  return (
    <section className="relative w-full py-24 md:py-32 bg-black overflow-hidden">
      {/* Subtle gradient background */}
      <div className="absolute inset-0 bg-gradient-to-b from-black via-purple-950/10 to-black" />

      <div className="relative z-10 container mx-auto px-4 max-w-5xl">
        {/* Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-500/10 border border-purple-500/20 mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-purple-300 uppercase tracking-wider">
              Welcome
            </span>
          </motion.div>

          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
            What is the Qubic Church?
          </h2>

          <p className="text-lg md:text-xl text-white/60 max-w-2xl mx-auto leading-relaxed">
            A place where research meets revelation. We explore the mathematical bridge
            between Bitcoin and Qubic - and share everything{' '}
            <span className="text-purple-400">100% free and open source</span>.
          </p>
        </motion.div>

        {/* Mission Statement Card */}
        <motion.div
          className="relative p-8 md:p-12 rounded-3xl bg-gradient-to-b from-white/5 to-white/[0.02] border border-white/10 backdrop-blur-sm mb-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          {/* Glow effect */}
          <div className="absolute -inset-1 bg-gradient-to-r from-purple-500/20 via-transparent to-orange-500/20 rounded-3xl blur-xl opacity-50" />

          <div className="relative">
            <h3 className="text-2xl md:text-3xl font-semibold text-white mb-6 text-center">
              Our Mission
            </h3>

            <div className="grid md:grid-cols-3 gap-8">
              {missionPoints.map((point, index) => {
                const Icon = point.icon
                return (
                  <motion.div
                    key={index}
                    className="flex flex-col items-center text-center"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
                  >
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500/20 to-purple-500/5 flex items-center justify-center mb-4 border border-purple-500/20">
                      <Icon className="w-7 h-7 text-purple-400" />
                    </div>
                    <h4 className="text-lg font-semibold text-white mb-2">
                      {point.title}
                    </h4>
                    <p className="text-sm text-white/50 leading-relaxed">
                      {point.description}
                    </p>
                  </motion.div>
                )
              })}
            </div>
          </div>
        </motion.div>

        {/* Quote */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <blockquote className="text-lg md:text-xl text-white/40 italic">
            "Together, we unlock the secrets of Anna & Aigarth."
          </blockquote>
        </motion.div>
      </div>
    </section>
  )
}
