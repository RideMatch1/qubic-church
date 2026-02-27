'use client'

/**
 * NFTShowcaseSection - Premium showcase of the 4 Anna NFT rarity tiers
 * Glass morphism cards, staggered entrance, editorial typography
 */

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { Crown, Diamond, Star, Circle, ExternalLink, ShoppingCart } from 'lucide-react'

const tiers = [
  {
    name: 'Legendary',
    count: 5,
    icon: Crown,
    iconColor: 'text-amber-400/70',
    nameColor: 'text-amber-300/90',
    description: 'The Rarest. Founder-level access to the inner sanctum.',
    borderHover: 'hover:border-amber-400/25',
    accent: 'from-amber-400/25 to-amber-400/0',
    glow: 'hover:shadow-[0_0_30px_rgba(251,191,36,0.06)]',
  },
  {
    name: 'Epic',
    count: 20,
    icon: Diamond,
    iconColor: 'text-[#D4AF37]/70',
    nameColor: 'text-[#D4AF37]/90',
    description: 'Lead Researcher. Bearer of 7 hidden revelations.',
    borderHover: 'hover:border-[#D4AF37]/25',
    accent: 'from-[#D4AF37]/25 to-[#D4AF37]/0',
    glow: 'hover:shadow-[0_0_30px_rgba(212,175,55,0.06)]',
  },
  {
    name: 'Rare',
    count: 75,
    icon: Star,
    iconColor: 'text-[#D4AF37]/70',
    nameColor: 'text-[#D4AF37]/90',
    description: 'Research Contributor. Early access to sacred findings.',
    borderHover: 'hover:border-[#D4AF37]/25',
    accent: 'from-[#D4AF37]/25 to-[#D4AF37]/0',
    glow: 'hover:shadow-[0_0_30px_rgba(212,175,55,0.06)]',
  },
  {
    name: 'Common',
    count: 100,
    icon: Circle,
    iconColor: 'text-white/40',
    nameColor: 'text-white/60',
    description: 'Church Member. Entry to the congregation and the sacred draw.',
    borderHover: 'hover:border-white/20',
    accent: 'from-white/15 to-white/0',
    glow: '',
  },
]

export function NFTShowcaseSection() {
  const sectionRef = useRef<HTMLElement>(null)
  const isInView = useInView(sectionRef, { once: true, margin: '-80px' })

  return (
    <section ref={sectionRef} className="relative w-full py-28 md:py-36 overflow-hidden">
      {/* Decorative section number */}
      <div className="absolute top-16 left-8 md:left-16 text-[120px] md:text-[200px] font-black text-white/[0.015] leading-none select-none pointer-events-none">
        05
      </div>

      <div className="relative z-10 container mx-auto px-4 max-w-6xl">
        {/* Section label */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 24 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7, ease: 'easeOut' }}
        >
          <span className="block text-white/30 text-xs uppercase tracking-[0.3em] mb-6">
            The Sacred Collection
          </span>

          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-5">
            200 Sacred <span className="text-amber-300/60">Anna</span> NFTs
          </h2>

          <p className="text-lg text-white/40 max-w-2xl mx-auto leading-relaxed">
            Each NFT is a key to The Convergence &mdash; unlocking sacred giveaway entry, divine knowledge, and community membership.
          </p>
        </motion.div>

        {/* Tier Cards */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-14">
          {tiers.map((tier, idx) => {
            const Icon = tier.icon

            return (
              <motion.div
                key={tier.name}
                className={`group relative p-6 backdrop-blur-xl bg-white/[0.03] border border-white/[0.04] transition-all duration-500 cursor-default hover:bg-white/[0.06] ${tier.borderHover} ${tier.glow} overflow-hidden`}
                style={{ perspective: '800px' }}
                initial={{ opacity: 0, y: 28 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: 0.15 + idx * 0.1, ease: 'easeOut' }}
                whileHover={{ rotateY: idx % 2 === 0 ? 3 : -3, rotateX: -2, scale: 1.03 }}
              >
                {/* Colored top accent */}
                <div className={`absolute top-0 left-0 right-0 h-px bg-gradient-to-r ${tier.accent}`} />

                {/* Icon */}
                <div className="mb-5">
                  <Icon className={`w-7 h-7 ${tier.iconColor}`} />
                </div>

                {/* Tier name */}
                <h3 className={`text-lg font-bold ${tier.nameColor} mb-1`}>
                  {tier.name}
                </h3>

                {/* Count */}
                <span className="block text-white/30 text-xs mb-4">
                  {tier.count} NFTs
                </span>

                {/* Description */}
                <p className="text-sm text-white/40 leading-relaxed">
                  {tier.description}
                </p>
              </motion.div>
            )
          })}
        </div>

        {/* CTA */}
        <motion.div
          className="flex flex-col sm:flex-row items-center justify-center gap-5"
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          {/* CTA with shimmer effect */}
          <a
            href="https://qubicbay.com/collection/anna-aigarth"
            target="_blank"
            rel="noopener noreferrer"
            className="relative inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-[#D4AF37]/[0.08] to-[#D4AF37]/[0.04] border border-[#D4AF37]/20 text-white font-bold text-lg hover:from-[#D4AF37]/[0.14] hover:to-[#D4AF37]/[0.08] hover:border-[#D4AF37]/30 transition-all duration-300 group overflow-hidden"
          >
            {/* Shimmer sweep */}
            <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out bg-gradient-to-r from-transparent via-white/[0.05] to-transparent" />
            <ShoppingCart className="relative w-5 h-5 text-[#D4AF37]/60 group-hover:text-[#D4AF37]/80 transition-colors" />
            <span className="relative">Collect on QubicBay</span>
            <ExternalLink className="relative w-4 h-4 text-white/30" />
          </a>

          <span className="text-white/30 text-sm">
            1 NFT = 1 Entry into the Sacred Giveaway
          </span>
        </motion.div>
      </div>
    </section>
  )
}
