'use client'

import { motion } from 'framer-motion'
import { BookOpen, Compass, Brain, Sparkles, Image as ImageIcon } from 'lucide-react'

const features = [
  {
    icon: BookOpen,
    title: 'The Archive',
    description: 'Complete research documentation connecting Bitcoin and Qubic through mathematical patterns',
    href: '/archives',
    color: 'from-orange-500 to-orange-600',
  },
  {
    icon: Compass,
    title: 'The Journey',
    description: 'An immersive story of discovery, tracing the investigation from genesis block to revelation',
    href: '/timeline',
    color: 'from-purple-500 to-purple-600',
  },
  {
    icon: Brain,
    title: 'Intelligence Challenges',
    description: 'Test your pattern recognition skills with cryptographic puzzles and earn role-based bonuses',
    href: '/challenges',
    color: 'from-blue-500 to-blue-600',
  },
  {
    icon: Sparkles,
    title: 'Holy Circle Lottery',
    description: 'Participate in the community lottery with Genesis address verification and transparent draws',
    href: '#lottery',
    color: 'from-cyan-500 to-cyan-600',
  },
  {
    icon: ImageIcon,
    title: 'Anna NFT Collection',
    description: '200 unique digital artifacts, each connected to specific research discoveries',
    href: 'https://qubicbay.io/collections/7',
    color: 'from-pink-500 to-pink-600',
    external: true,
  },
]

export function ChurchIntroSection() {
  return (
    <section className="relative min-h-[80vh] flex items-center justify-center py-20 md:py-32 bg-gradient-to-b from-[#050505] via-[#D4AF37]/5 to-[#050505]">
      {/* Background gradient glow */}
      <div className="absolute inset-0 bg-gradient-radial from-[#D4AF37]/5 via-transparent to-transparent pointer-events-none" />

      <div className="relative z-10 container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/[0.04] mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Sparkles className="w-4 h-4 text-[#D4AF37]" />
            <span className="text-sm text-white/70 uppercase tracking-wider">Welcome</span>
          </motion.div>

          <h2 className="text-4xl md:text-6xl font-bold text-white/90 mb-6">
            The Qubic Church
          </h2>

          <p className="text-lg md:text-xl text-white/60 max-w-2xl mx-auto leading-relaxed">
            A sanctuary where research meets revelation.
            <span className="text-white/80"> Exploring the mathematical bridge between Bitcoin and Qubic.</span>
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <motion.a
                key={feature.title}
                href={feature.href}
                target={feature.external ? '_blank' : undefined}
                rel={feature.external ? 'noopener noreferrer' : undefined}
                className="group relative p-6 bg-[#050505]/80 backdrop-blur-xl border border-white/[0.04] hover:border-white/20 transition-all duration-300 hover:scale-105"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                {/* Gradient glow on hover */}
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300 blur-xl`} />

                <div className="relative">
                  {/* Icon */}
                  <div className={`inline-flex p-3 bg-gradient-to-br ${feature.color} mb-4`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>

                  {/* Title */}
                  <h3 className="text-xl font-semibold text-white/90 mb-2 group-hover:text-white transition-colors">
                    {feature.title}
                  </h3>

                  {/* Description */}
                  <p className="text-sm text-white/50 leading-relaxed group-hover:text-white/60 transition-colors">
                    {feature.description}
                  </p>

                  {/* External link indicator */}
                  {feature.external && (
                    <div className="mt-3 inline-flex items-center gap-1 text-xs text-white/40 group-hover:text-white/60 transition-colors">
                      <span>View External</span>
                      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </div>
                  )}
                </div>
              </motion.a>
            )
          })}
        </div>

        {/* Bottom tagline */}
        <motion.div
          className="text-center mt-16"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <p className="text-white/40 text-sm italic">
            "All research is 100% free and open source. Join the investigation."
          </p>
        </motion.div>
      </div>
    </section>
  )
}
